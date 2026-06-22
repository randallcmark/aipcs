#!/usr/bin/env python3
"""Combine multiple AIPCS snapshot .data directories into one snapshot.

This is intentionally mechanical: it preserves services and service databases
as authored, merges registry rows, and rewrites registry endpoints so the
combined snapshot can be inspected in place. Lab imports still need the normal
owner/path rewrite from owner "mark" to owner "lab".
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("inputs", nargs="+", type=Path)
    return parser.parse_args()


def registry_path(root: Path) -> Path:
    data_root = root / ".data" if root.name != ".data" else root
    return data_root / "aipcs-registry.sqlite"


def data_root(root: Path) -> Path:
    return root if root.name == ".data" else root / ".data"


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def copy_registry_schema(source_registry: Path, output_registry: Path) -> None:
    output_registry.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_registry, output_registry)
    with sqlite3.connect(output_registry) as con:
        con.execute("delete from audit_log")
        con.execute("delete from services")
        con.commit()


def table_columns(con: sqlite3.Connection, table_name: str) -> list[str]:
    return [row[1] for row in con.execute(f"pragma table_info({quote_identifier(table_name)})")]


def insert_row(
    destination: sqlite3.Connection,
    table_name: str,
    columns: list[str],
    values: sqlite3.Row,
    overrides: dict[str, object] | None = None,
) -> None:
    overrides = overrides or {}
    payload = [overrides.get(column, values[column]) for column in columns]
    column_sql = ", ".join(quote_identifier(column) for column in columns)
    placeholder_sql = ", ".join("?" for _ in columns)
    destination.execute(
        f"insert into {quote_identifier(table_name)} ({column_sql}) values ({placeholder_sql})",
        payload,
    )


def merge_snapshot(input_root: Path, output_root: Path, seen_service_ids: set[str]) -> None:
    input_data = data_root(input_root)
    input_registry = input_data / "aipcs-registry.sqlite"
    output_registry = output_root / "aipcs-registry.sqlite"

    if not input_registry.exists():
        raise FileNotFoundError(f"Missing registry: {input_registry}")

    with sqlite3.connect(input_registry) as src, sqlite3.connect(output_registry) as dst:
        src.row_factory = sqlite3.Row
        dst.row_factory = sqlite3.Row

        service_columns = table_columns(src, "services")
        audit_columns = [column for column in table_columns(src, "audit_log") if column != "id"]

        services = list(src.execute("select * from services order by domain_name"))
        for service in services:
            service_id = service["service_id"]
            domain_name = service["domain_name"]
            if service_id in seen_service_ids:
                raise ValueError(f"Duplicate service_id {service_id} from {input_root}")
            seen_service_ids.add(service_id)

            source_service_dir = input_data / "services" / service_id
            target_service_dir = output_root / "services" / service_id
            if not source_service_dir.exists():
                raise FileNotFoundError(f"Missing service directory: {source_service_dir}")
            shutil.copytree(source_service_dir, target_service_dir)

            endpoint = f"sqlite:///{target_service_dir / f'{domain_name}.sqlite'}"
            insert_row(dst, "services", service_columns, service, {"endpoint": endpoint})

        for audit in src.execute("select * from audit_log order by id"):
            insert_row(dst, "audit_log", audit_columns, audit)

        dst.commit()


def main() -> None:
    args = parse_args()
    output_data = data_root(args.output)

    if output_data.exists():
        if not args.force:
            raise FileExistsError(f"Output exists; pass --force to replace: {output_data}")
        shutil.rmtree(output_data)

    input_registries = [registry_path(path) for path in args.inputs]
    missing = [path for path in input_registries if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing input registries: {missing}")

    copy_registry_schema(input_registries[0], output_data / "aipcs-registry.sqlite")

    seen_service_ids: set[str] = set()
    for input_root in args.inputs:
        merge_snapshot(input_root, output_data, seen_service_ids)

    print(f"combined {len(args.inputs)} snapshots into {output_data}")
    print(f"services: {len(seen_service_ids)}")


if __name__ == "__main__":
    main()
