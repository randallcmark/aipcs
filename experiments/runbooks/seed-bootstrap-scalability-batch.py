"""Seed controlled AIPCS bootstrap/orientation scalability scenarios.

Run this inside the aipcs-lab-server container for a fresh run-local AIPCS
store. The script uses the server's public tool layer rather than writing
SQLite directly.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any

from aipcs_server.config import load_config
from aipcs_server.registry import Registry
from aipcs_server.tools import AipcsTools


@dataclass(frozen=True)
class Scenario:
    run_id: str
    purpose: str
    service_count: int
    entities_per_service: int
    extra_attrs_per_entity: int
    records_per_entity: int
    verbosity: str
    target_service_indexes: tuple[int, ...]


SCENARIOS: dict[str, Scenario] = {
    "run018": Scenario(
        run_id="run018",
        purpose="Synthetic small control for bootstrap/orientation scoring.",
        service_count=3,
        entities_per_service=2,
        extra_attrs_per_entity=2,
        records_per_entity=5,
        verbosity="compact",
        target_service_indexes=(1, 2),
    ),
    "run019": Scenario(
        run_id="run019",
        purpose="Service breadth stress: many compact services with low schema depth.",
        service_count=25,
        entities_per_service=2,
        extra_attrs_per_entity=2,
        records_per_entity=5,
        verbosity="compact",
        target_service_indexes=(7, 18),
    ),
    "run020": Scenario(
        run_id="run020",
        purpose="Schema verbosity stress: fewer services, rich entities, verbose attribute descriptions.",
        service_count=5,
        entities_per_service=5,
        extra_attrs_per_entity=12,
        records_per_entity=5,
        verbosity="verbose",
        target_service_indexes=(2, 4),
    ),
    "run021": Scenario(
        run_id="run021",
        purpose="Record volume stress: manageable bootstrap shape with larger record tables.",
        service_count=5,
        entities_per_service=2,
        extra_attrs_per_entity=2,
        records_per_entity=100,
        verbosity="normal",
        target_service_indexes=(1, 3),
    ),
}


DOMAIN_CLASSES = [
    "research_planning",
    "lab_operations",
    "paper_positioning",
    "agent_behavior",
    "personal_context",
    "implementation_context",
    "media",
    "travel",
    "finance",
    "health",
    "home",
    "learning",
    "project_tracking",
    "authority_context",
    "reviewer_feedback",
    "background_material",
]


def make_tools() -> AipcsTools:
    config = load_config()
    registry = Registry(config.db_path, services_dir=config.services_dir)
    return AipcsTools(registry=registry, owner_id=config.owner_id)


def description(text: str, verbosity: str) -> str:
    if verbosity == "compact":
        return text
    if verbosity == "normal":
        return (
            f"{text} Use this field for bounded recall and filtering. "
            "Prefer short values that help an agent decide whether the record applies."
        )
    return (
        f"{text} This deliberately verbose description exists for bootstrap scalability testing. "
        "It describes how the field should be interpreted, when the field should influence "
        "retrieval, and why an agent may need to inspect the service before answering. "
        "The content is intentionally repetitive so the experiment can measure whether schema "
        "verbosity alone makes the orientation payload too costly or difficult to consume."
    )


def base_attributes(verbosity: str, extra_count: int) -> list[dict[str, Any]]:
    attrs: list[dict[str, Any]] = [
        {"name": "id", "type": "uuid", "primary_key": True},
        {"name": "owner_id", "type": "string", "required": True},
        {
            "name": "record_id",
            "type": "string",
            "required": True,
            "description": description("Stable scenario-local record identifier.", verbosity),
        },
        {
            "name": "topic",
            "type": "string",
            "required": True,
            "description": description("Retrieval topic for exact filtering.", verbosity),
        },
        {
            "name": "summary",
            "type": "string",
            "required": True,
            "description": description("Short retrievable fact or observation.", verbosity),
        },
        {
            "name": "detail",
            "type": "string",
            "description": description("Optional supporting explanation.", verbosity),
        },
        {
            "name": "source_type",
            "type": "string",
            "required": True,
            "allowed_values": [
                "synthetic_ground_truth",
                "synthetic_distractor",
                "synthetic_background",
                "synthetic_conflict",
            ],
            "description": description("Provenance class for scoring.", verbosity),
        },
        {
            "name": "status",
            "type": "string",
            "required": True,
            "allowed_values": ["active", "background", "stale", "candidate", "distractor"],
            "description": description("Lifecycle status used for authority weighting.", verbosity),
        },
        {
            "name": "priority",
            "type": "string",
            "required": True,
            "allowed_values": ["low", "medium", "high"],
            "description": description("Importance signal for answer construction.", verbosity),
        },
    ]

    for i in range(1, extra_count + 1):
        attrs.append(
            {
                "name": f"dimension_{i:02d}",
                "type": "string",
                "description": description(
                    f"Synthetic dimensional field {i:02d} used to vary schema width.",
                    verbosity,
                ),
            }
        )

    attrs.extend(
        [
            {"name": "created_at", "type": "datetime", "required": True},
            {"name": "updated_at", "type": "datetime", "required": True},
            {"name": "created_via", "type": "string", "required": True},
        ]
    )
    return attrs


def make_schema(scenario: Scenario, service_index: int) -> tuple[dict[str, Any], list[str]]:
    entities: list[dict[str, Any]] = []
    entity_names: list[str] = []
    for entity_index in range(1, scenario.entities_per_service + 1):
        entity_name = f"note_{entity_index:02d}"
        entity_names.append(entity_name)
        entities.append(
            {
                "name": entity_name,
                "description": description(
                    f"Synthetic entity {entity_index:02d} for service {service_index:02d}.",
                    scenario.verbosity,
                ),
                "attributes": base_attributes(scenario.verbosity, scenario.extra_attrs_per_entity),
            }
        )

    return (
        {
            "schema_version": 1,
            "entities": entities,
            "relationships": [],
            "indices": [
                {"entity": entity_name, "fields": ["owner_id", "topic"]}
                for entity_name in entity_names
            ],
            "query_patterns": [
                f"list records in {entity_name} by topic and status"
                for entity_name in entity_names
            ],
            "migration_history": [],
        },
        entity_names,
    )


def service_name(run_id: str, index: int) -> str:
    domain = DOMAIN_CLASSES[(index - 1) % len(DOMAIN_CLASSES)]
    return f"{run_id}_{index:02d}_{domain}"


def make_record(
    scenario: Scenario,
    service_index: int,
    entity_name: str,
    record_index: int,
    is_target_service: bool,
    is_primary_target: bool,
) -> dict[str, Any]:
    record_id = f"{scenario.run_id.upper()}-S{service_index:02d}-{entity_name.upper()}-R{record_index:03d}"

    if is_primary_target and record_index == 3:
        topic = "orientation_scalability_next_step"
        summary = (
            "The next paper-relevant action is to measure bootstrap/orientation scalability "
            "before broad comparator work."
        )
        detail = (
            "This is the controlled ground-truth target. A good answer should recommend "
            "continuing the orientation scalability ladder and cite AIPCS-derived context."
        )
        source_type = "synthetic_ground_truth"
        status = "active"
        priority = "high"
    elif is_target_service and record_index == 4:
        topic = "cost_value_accounting"
        summary = (
            "Memory overhead must be judged against value delivered, including missed-service "
            "avoidance, false-positive resistance, and reduced user re-explanation."
        )
        detail = (
            "This supporting target should be combined with the orientation target rather than "
            "treated as a separate next step."
        )
        source_type = "synthetic_ground_truth"
        status = "active"
        priority = "high"
    else:
        topic = f"background_topic_{(service_index + record_index) % 9:02d}"
        summary = (
            f"Background note {record_index:03d} for service {service_index:02d}; plausible "
            "but not decisive for the current decision prompt."
        )
        detail = (
            "This record exists to create retrieval pressure. It should not override active "
            "ground-truth orientation or cost-value records."
        )
        source_type = "synthetic_background" if record_index % 3 else "synthetic_distractor"
        status = "background" if record_index % 4 else "distractor"
        priority = "low" if record_index % 5 else "medium"

    record: dict[str, Any] = {
        "record_id": record_id,
        "topic": topic,
        "summary": summary,
        "detail": detail,
        "source_type": source_type,
        "status": status,
        "priority": priority,
    }
    for i in range(1, scenario.extra_attrs_per_entity + 1):
        record[f"dimension_{i:02d}"] = f"{scenario.run_id}:s{service_index:02d}:{entity_name}:d{i:02d}"
    return record


def seed_service(tools: AipcsTools, scenario: Scenario, service_index: int) -> dict[str, Any]:
    name = service_name(scenario.run_id, service_index)
    domain_class = DOMAIN_CLASSES[(service_index - 1) % len(DOMAIN_CLASSES)]
    is_target = service_index in scenario.target_service_indexes
    intent = (
        f"Synthetic {scenario.run_id} service {service_index:02d} for bootstrap scalability. "
        f"Domain class: {domain_class}."
    )
    if scenario.verbosity == "verbose":
        intent += (
            " This service has intentionally verbose schema metadata so the experiment can "
            "measure whether orientation payload size degrades agent service selection."
        )

    seed = tools.aipcs_service_seed(
        domain_name=name,
        domain_class=domain_class,
        intent_description=intent,
    )
    service_id = seed["service"]["service_id"]
    if seed.get("duplicate"):
        raise RuntimeError(f"Service {name} already exists; reset AIPCS state before reseeding.")

    schema, entity_names = make_schema(scenario, service_index)
    design = tools.aipcs_service_design(service_id=service_id, schema=schema)
    materialise = tools.aipcs_service_materialise(service_id=service_id)

    created = 0
    target_records: list[dict[str, str]] = []
    primary_target_service = service_index == scenario.target_service_indexes[0]
    for entity_name in entity_names:
        for record_index in range(1, scenario.records_per_entity + 1):
            record = make_record(
                scenario,
                service_index,
                entity_name,
                record_index,
                is_target,
                primary_target_service,
            )
            result = tools.aipcs_record_create(
                service_id=service_id,
                entity_name=entity_name,
                record=record,
                created_via="codex_admin_seed",
            )
            created += 1
            if record["source_type"] == "synthetic_ground_truth":
                target_records.append(
                    {
                        "service": name,
                        "entity": entity_name,
                        "record_id": record["record_id"],
                        "topic": record["topic"],
                    }
                )
            if not result.get("created"):
                raise RuntimeError(f"Record create failed for {record['record_id']}: {result}")

    return {
        "domain_name": name,
        "service_id": service_id,
        "domain_class": domain_class,
        "entity_count": len(entity_names),
        "record_count": created,
        "target_record_count": len(target_records),
        "target_records": target_records,
        "design_accepted": design.get("accepted"),
        "materialised": materialise.get("materialised"),
    }


def seed_scenario(scenario: Scenario) -> dict[str, Any]:
    tools = make_tools()
    services = [
        seed_service(tools=tools, scenario=scenario, service_index=index)
        for index in range(1, scenario.service_count + 1)
    ]
    return {
        "run": scenario.run_id,
        "corpus_family": "controlled_synthetic",
        "purpose": scenario.purpose,
        "scale_factors": {
            "service_count": scenario.service_count,
            "entities_per_service": scenario.entities_per_service,
            "extra_attrs_per_entity": scenario.extra_attrs_per_entity,
            "records_per_entity": scenario.records_per_entity,
            "schema_verbosity": scenario.verbosity,
        },
        "expected_prompt": (
            "I need to make a decision based on what is already known. Review the "
            "available context and recommend the next step, citing what shaped your answer."
        ),
        "expected_answer": {
            "primary": "Recommend continuing bootstrap/orientation scalability measurement.",
            "supporting": "Include cost/value accounting rather than treating memory overhead as free.",
            "should_not_prioritise": [
                "OpenWebUI integration",
                "agent-memory-v2 comparison before AIPCS orientation behavior is understood",
                "generic paper work without citing AIPCS-retrieved context",
            ],
        },
        "services": services,
        "service_count": len(services),
        "record_count": sum(service["record_count"] for service in services),
        "target_records": [
            target
            for service in services
            for target in service["target_records"]
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scenario",
        choices=sorted(SCENARIOS),
        help="Scenario/run id to seed into the active AIPCS data directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = seed_scenario(SCENARIOS[args.scenario])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
