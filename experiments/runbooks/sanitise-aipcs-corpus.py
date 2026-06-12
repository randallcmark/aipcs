#!/usr/bin/env python3
"""Create a fictionalised AIPCS corpus from a private organic data directory.

The script preserves service/entity/table shape, record counts, timestamps at a
coarse synthetic level, and relationship topology where obvious slug references
exist. It does not copy raw SQLite files. Each output database is rebuilt from
schema and populated with generated values so raw content is not left behind in
SQLite free pages.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any


SERVICE_INTENTS = {
    "aipcs_development": "Fictional software research memory for AIPCS-style evaluation work.",
    "claude_memory": "Fictional agent collaboration memory used for cross-session recall tests.",
    "cooking": "Fictional cooking, pantry, meal, and dietary preference memory.",
    "health_fitness": "Fictional wellness and fitness tracking memory with non-real values.",
    "household": "Fictional household maintenance, possession, provider, and supply memory.",
    "media_learning": "Fictional media and learning memory with synthetic titles and notes.",
    "people": "Fictional personal CRM memory with invented contacts and interactions.",
    "personal_finance": "Fictional finance memory with non-real institutions and amounts.",
    "personal_preferences": "Fictional user preference memory for recall-quality experiments.",
    "technical_knowledge": "Fictional technical knowledge memory with generated commands and snippets.",
    "travel": "Fictional travel memory with invented trips, places, and preferences.",
}

FIRST_NAMES = [
    "Avery",
    "Blair",
    "Casey",
    "Devon",
    "Ellis",
    "Finley",
    "Harper",
    "Jordan",
    "Morgan",
    "Riley",
    "Rowan",
    "Taylor",
]
LAST_NAMES = [
    "Vale",
    "Quinn",
    "Hart",
    "Stone",
    "Lane",
    "Reed",
    "Marlow",
    "Ash",
    "Keane",
    "Wren",
]
FICTIONAL_CITIES = [
    ("Larkhaven", "UK"),
    ("Northbridge", "UK"),
    ("Mossford", "Ireland"),
    ("Veyra", "Portugal"),
    ("Riverton", "Canada"),
    ("Halewick", "Netherlands"),
    ("Greyport", "Sweden"),
    ("Sable Bay", "New Zealand"),
]
TOPICS = [
    "memory discovery",
    "schema clarity",
    "evaluation repeatability",
    "operator workflow",
    "retrieval friction",
    "source authority",
    "corpus growth",
    "agent autonomy",
]


@dataclass(frozen=True)
class TableContext:
    service: str
    table: str
    row_index: int
    row_count: int


def stable_int(*parts: object) -> int:
    h = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(h[:12], 16)


def stable_uuid(namespace: str, value: str) -> str:
    return str(uuid.uuid5(uuid.uuid5(uuid.NAMESPACE_URL, namespace), value))


def synthetic_date(ctx: TableContext, column: str) -> str:
    base = date(2025, 1, 6)
    day = stable_int(ctx.service, ctx.table, column, ctx.row_index) % 520
    return (base + timedelta(days=day)).isoformat()


def synthetic_datetime(ctx: TableContext, column: str) -> str:
    d = synthetic_date(ctx, column)
    minute = stable_int(ctx.service, ctx.table, column, "minute", ctx.row_index) % (24 * 60)
    hour, minute = divmod(minute, 60)
    return f"{d}T{hour:02d}:{minute:02d}:00Z"


def choice(options: list[str], ctx: TableContext, column: str) -> str:
    return options[stable_int(ctx.service, ctx.table, column, ctx.row_index) % len(options)]


def synthetic_slug(ctx: TableContext, prefix: str | None = None) -> str:
    clean_prefix = (prefix or ctx.table).replace("_", "-")
    return f"{clean_prefix}-{ctx.row_index:03d}"


def synthetic_name(ctx: TableContext) -> str:
    first = FIRST_NAMES[stable_int(ctx.service, ctx.table, "first", ctx.row_index) % len(FIRST_NAMES)]
    last = LAST_NAMES[stable_int(ctx.service, ctx.table, "last", ctx.row_index) % len(LAST_NAMES)]
    return f"{first} {last}"


def synthetic_title(ctx: TableContext, noun: str | None = None) -> str:
    topic = choice(TOPICS, ctx, "topic")
    base = noun or ctx.table.replace("_", " ")
    return f"{base.title()} {ctx.row_index:03d}: {topic.title()}"


def synthetic_sentence(ctx: TableContext, column: str) -> str:
    topic = choice(TOPICS, ctx, column)
    return (
        f"Fictional {ctx.service.replace('_', ' ')} note {ctx.row_index:03d} "
        f"about {topic}; generated for sanitised AIPCS recall experiments."
    )


def synthetic_code(ctx: TableContext) -> str:
    return (
        "def synthetic_example(value: str) -> str:\n"
        f"    return f\"{ctx.table}-{ctx.row_index:03d}: {{value}}\"\n"
    )


def synthetic_amount(ctx: TableContext, column: str) -> str:
    amount = 8 + (stable_int(ctx.service, ctx.table, column, ctx.row_index) % 1800)
    pence = stable_int(ctx.service, ctx.table, column, "pence", ctx.row_index) % 100
    return f"{amount}.{pence:02d}"


def load_rows(con: sqlite3.Connection, table: str) -> tuple[list[str], list[sqlite3.Row]]:
    con.row_factory = sqlite3.Row
    cols = [r[1] for r in con.execute(f'pragma table_info("{table}")').fetchall()]
    rows = con.execute(f'select * from "{table}" order by rowid').fetchall()
    return cols, rows


def create_schema(source: sqlite3.Connection, target: sqlite3.Connection) -> None:
    for (sql,) in source.execute(
        "select sql from sqlite_master where type='table' and name not like 'sqlite_%' and sql is not null order by name"
    ).fetchall():
        target.execute(sql)
    target.commit()


def service_table_names(con: sqlite3.Connection) -> list[str]:
    return [
        r[0]
        for r in con.execute(
            "select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name"
        ).fetchall()
    ]


def build_slug_maps(db_path: Path, service_name: str) -> dict[str, dict[str, str]]:
    maps: dict[str, dict[str, str]] = {}
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        for table in service_table_names(con):
            if table == "aipcs_record_history":
                continue
            cols, rows = load_rows(con, table)
            for index, row in enumerate(rows, start=1):
                ctx = TableContext(service_name, table, index, len(rows))
                if "id" in cols:
                    maps.setdefault(f"{table}.id", {})[str(row["id"])] = synthetic_slug(ctx, table)
                if "slug" in cols and row["slug"] is not None:
                    maps.setdefault(f"{table}.slug", {})[str(row["slug"])] = synthetic_slug(ctx, table)
    finally:
        con.close()
    return maps


def resolve_reference(value: Any, column: str, maps: dict[str, dict[str, str]], ctx: TableContext) -> str:
    if value is None:
        return ""
    original = str(value)
    reference_table = {
        "contact_slug": "contact.slug",
        "item_slug": "possession.slug",
        "trip_slug": "trip.slug",
        "media_slug": "media_item.slug",
        "recipe_slug": "recipe.slug",
    }.get(column)
    if reference_table and original in maps.get(reference_table, {}):
        return maps[reference_table][original]
    return synthetic_slug(ctx, column.removesuffix("_slug"))


def sanitise_registry_json(value: str | None, service_name: str) -> str | None:
    if value in (None, ""):
        return value
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return json.dumps({"sanitised": True, "note": f"Fictional metadata for {service_name}."})

    def walk(item: Any) -> Any:
        if isinstance(item, dict):
            return {k: walk(v) for k, v in item.items()}
        if isinstance(item, list):
            return [walk(v) for v in item]
        if isinstance(item, str):
            if len(item) > 32 or " " in item:
                return f"Fictional {service_name} metadata."
            return item
        return item

    return json.dumps(walk(parsed), sort_keys=True)


def sanitise_value(
    value: Any,
    column: str,
    ctx: TableContext,
    maps: dict[str, dict[str, str]],
    declared_type: str,
    owner_id: str,
) -> Any:
    col = column.lower()
    if col == "owner_id":
        return owner_id
    if col == "id":
        return synthetic_slug(ctx, ctx.table)
    if col == "history_id":
        return f"hist-{ctx.table}-{ctx.row_index:04d}"
    if col == "record_id":
        return f"record-{ctx.row_index:04d}"
    if col == "slug":
        return synthetic_slug(ctx, ctx.table)
    if col.endswith("_slug"):
        return resolve_reference(value, col, maps, ctx)
    if col in {"created_at", "updated_at", "changed_at", "materialised_at"}:
        return synthetic_datetime(ctx, col)
    if col.endswith("_on") or col.endswith("_date") or col == "date" or col in {"birthday", "renewal_date"}:
        return synthetic_date(ctx, col)
    if col in {"before_json", "after_json", "payload_json", "schema_manifest_json", "tools_json", "aliases_json"}:
        return json.dumps(
            {
                "sanitised": True,
                "service": ctx.service,
                "entity": ctx.table,
                "record": ctx.row_index,
            },
            sort_keys=True,
        )
    if "amount" in col or "cost" in col or "price" in col or "target" in col:
        return synthetic_amount(ctx, col)
    if col == "currency":
        return "GBP"
    if declared_type.upper().startswith("INTEGER"):
        return 1 + (stable_int(ctx.service, ctx.table, col, ctx.row_index) % 9)
    if col in {"rating", "severity", "strength", "priority", "intensity", "closeness"}:
        return choice(["low", "medium", "high"], ctx, col)
    if col in {"status", "state"}:
        return choice(["active", "pending", "resolved", "archived"], ctx, col)
    if col in {"polarity", "recommend", "would_return", "recurring", "follow_up_needed"}:
        return choice(["positive", "neutral", "negative"], ctx, col)
    if col in {"full_name", "provider_name", "name", "creator"}:
        if ctx.table == "contact" or "provider" in col:
            return synthetic_name(ctx)
        return synthetic_title(ctx, col)
    if col in {"title", "summary", "statement", "description", "rationale", "reason", "outcome", "detail"}:
        return synthetic_sentence(ctx, col)
    if col in {"notes", "body", "why", "how_to_apply", "context", "highlights"}:
        return synthetic_sentence(ctx, col)
    if col in {"location", "city", "destination"}:
        return FICTIONAL_CITIES[stable_int(ctx.service, ctx.table, col, ctx.row_index) % len(FICTIONAL_CITIES)][0]
    if col == "country":
        return FICTIONAL_CITIES[stable_int(ctx.service, ctx.table, col, ctx.row_index) % len(FICTIONAL_CITIES)][1]
    if col in {"employer_role", "institution", "merchant", "brand", "model", "typical_store"}:
        return f"Fictional {col.replace('_', ' ')} {ctx.row_index:03d}"
    if col in {"code", "command"}:
        return synthetic_code(ctx) if col == "code" else f"synthetic-tool --record {ctx.row_index:03d}"
    if col in {"tags", "topics", "interests", "key_ingredients", "dietary_tags", "companions", "household"}:
        return ", ".join(
            [
                choice(TOPICS, ctx, f"{col}-a"),
                choice(TOPICS, ctx, f"{col}-b"),
            ]
        )
    if value is None:
        return None
    return synthetic_sentence(ctx, col)


def sanitise_service_db(source_db: Path, target_db: Path, service_name: str, owner_id: str) -> dict[str, int]:
    target_db.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(source_db)
    source.row_factory = sqlite3.Row
    target = sqlite3.connect(target_db)
    counts: dict[str, int] = {}
    maps = build_slug_maps(source_db, service_name)
    try:
        create_schema(source, target)
        for table in service_table_names(source):
            col_info = source.execute(f'pragma table_info("{table}")').fetchall()
            cols = [r[1] for r in col_info]
            types = {r[1]: r[2] or "TEXT" for r in col_info}
            rows = source.execute(f'select * from "{table}" order by rowid').fetchall()
            counts[table] = len(rows)
            if not rows:
                continue
            placeholders = ", ".join(["?"] * len(cols))
            quoted_cols = ", ".join(f'"{c}"' for c in cols)
            for index, row in enumerate(rows, start=1):
                ctx = TableContext(service_name, table, index, len(rows))
                values = [sanitise_value(row[c], c, ctx, maps, types[c], owner_id) for c in cols]
                target.execute(f'insert into "{table}" ({quoted_cols}) values ({placeholders})', values)
        target.commit()
    finally:
        source.close()
        target.close()
    return counts


def sanitise_registry(
    source_data: Path,
    output_data: Path,
    service_id_map: dict[str, str],
    owner_id: str,
) -> list[dict[str, Any]]:
    source_db = source_data / "aipcs-registry.sqlite"
    target_db = output_data / "aipcs-registry.sqlite"
    source = sqlite3.connect(source_db)
    source.row_factory = sqlite3.Row
    target = sqlite3.connect(target_db)
    service_manifest: list[dict[str, Any]] = []
    try:
        create_schema(source, target)
        service_cols = [r[1] for r in source.execute('pragma table_info("services")').fetchall()]
        insert_cols = ", ".join(f'"{c}"' for c in service_cols)
        placeholders = ", ".join(["?"] * len(service_cols))
        for row in source.execute('select * from "services" order by domain_name').fetchall():
            domain_name = row["domain_name"]
            sanitised_service_id = service_id_map[row["service_id"]]
            ctx = TableContext(domain_name, "services", len(service_manifest) + 1, 1)
            values = []
            for col in service_cols:
                if col == "service_id":
                    values.append(sanitised_service_id)
                elif col == "owner_id":
                    values.append(owner_id)
                elif col == "intent_description":
                    values.append(SERVICE_INTENTS.get(domain_name, f"Fictional memory service for {domain_name}."))
                elif col == "aliases_json":
                    values.append(json.dumps([domain_name, domain_name.replace("_", " ")]))
                elif col == "schema_manifest_json":
                    values.append(sanitise_registry_json(row[col], domain_name))
                elif col == "tools_json":
                    values.append(sanitise_registry_json(row[col], domain_name))
                elif col == "endpoint":
                    db_name = f"{domain_name}.sqlite"
                    values.append(f"sqlite:////data/services/{sanitised_service_id}/{db_name}")
                elif col == "parent_service_id" and row[col] in service_id_map:
                    values.append(service_id_map[row[col]])
                elif col in {"created_at", "updated_at", "last_activity_at", "materialised_at"}:
                    values.append(synthetic_datetime(ctx, col) if row[col] else None)
                else:
                    values.append(row[col])
            target.execute(f'insert into "services" ({insert_cols}) values ({placeholders})', values)
            service_manifest.append(
                {
                    "service": domain_name,
                    "source_service_id": row["service_id"],
                    "sanitised_service_id": sanitised_service_id,
                    "state": row["state"],
                    "domain_class": row["domain_class"],
                }
            )

        audit_cols = [r[1] for r in source.execute('pragma table_info("audit_log")').fetchall()]
        insert_cols = ", ".join(f'"{c}"' for c in audit_cols)
        placeholders = ", ".join(["?"] * len(audit_cols))
        for index, row in enumerate(source.execute('select * from "audit_log" order by id').fetchall(), start=1):
            ctx = TableContext("registry", "audit_log", index, 1)
            values = []
            for col in audit_cols:
                if col == "id":
                    values.append(index)
                elif col == "owner_id":
                    values.append(owner_id)
                elif col == "service_id" and row[col] in service_id_map:
                    values.append(service_id_map[row[col]])
                elif col == "payload_json":
                    values.append(
                        json.dumps(
                            {
                                "sanitised": True,
                                "action": row["action"],
                                "source": "registry_audit_log",
                            },
                            sort_keys=True,
                        )
                    )
                elif col == "created_at":
                    values.append(synthetic_datetime(ctx, col))
                else:
                    values.append(row[col])
            target.execute(f'insert into "audit_log" ({insert_cols}) values ({placeholders})', values)
        target.commit()
    finally:
        source.close()
        target.close()
    return service_manifest


def discover_service_dbs(source_data: Path) -> dict[str, Path]:
    service_dir = source_data / "services"
    return {p.parent.name: p for p in sorted(service_dir.glob("*/*.sqlite"))}


def build_service_id_map(source_data: Path) -> dict[str, str]:
    con = sqlite3.connect(source_data / "aipcs-registry.sqlite")
    try:
        return {
            row[0]: stable_uuid("aipcs-sanitised-organic-service", row[0])
            for row in con.execute('select service_id from "services" order by service_id').fetchall()
        }
    finally:
        con.close()


def write_manifest(
    output_data: Path,
    services: list[dict[str, Any]],
    counts: dict[str, dict[str, int]],
    owner_id: str,
) -> None:
    total_records = sum(
        count
        for service_counts in counts.values()
        for table, count in service_counts.items()
        if table != "aipcs_record_history"
    )
    manifest = {
        "name": "sanitised-organic-v1",
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "sanitised": True,
        "owner_id": owner_id,
        "total_services": len(services),
        "total_non_history_records": total_records,
        "services": [
            {
                **{k: v for k, v in service.items() if not k.startswith("source_")},
                "tables": counts.get(service["service"], {}),
            }
            for service in services
        ],
        "privacy_note": (
            "Generated from private organic AIPCS shape. Raw record content was not copied; "
            "fresh SQLite files were created from schema and synthetic row values."
        ),
    }
    (output_data / "SANITISED_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-data", required=True, type=Path, help="Path to private source .data directory")
    parser.add_argument("--output-data", required=True, type=Path, help="Path to write fresh sanitised .data directory")
    parser.add_argument(
        "--owner-id",
        default="lab",
        help="Owner ID to write into the sanitised registry and service records. Defaults to the lab compose owner.",
    )
    parser.add_argument("--force", action="store_true", help="Remove existing output directory before writing")
    args = parser.parse_args()

    source_data = args.source_data.expanduser().resolve()
    output_data = args.output_data.expanduser().resolve()
    if not (source_data / "aipcs-registry.sqlite").exists():
        raise SystemExit(f"source does not look like an AIPCS .data directory: {source_data}")
    if output_data.exists():
        if not args.force:
            raise SystemExit(f"output exists; pass --force to replace: {output_data}")
        shutil.rmtree(output_data)
    output_data.mkdir(parents=True)

    service_id_map = build_service_id_map(source_data)
    service_manifest = sanitise_registry(source_data, output_data, service_id_map, args.owner_id)
    source_dbs = discover_service_dbs(source_data)
    counts: dict[str, dict[str, int]] = {}
    service_name_by_source_id = {item["source_service_id"]: item["service"] for item in service_manifest}
    for source_service_id, source_db in source_dbs.items():
        service_name = service_name_by_source_id.get(source_service_id, source_db.stem)
        target_service_id = service_id_map.get(
            source_service_id,
            stable_uuid("aipcs-sanitised-organic-service", source_service_id),
        )
        target_db = output_data / "services" / target_service_id / source_db.name
        counts[service_name] = sanitise_service_db(source_db, target_db, service_name, args.owner_id)

    write_manifest(output_data, service_manifest, counts, args.owner_id)
    print(json.dumps({"output_data": str(output_data), "services": len(service_manifest)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
