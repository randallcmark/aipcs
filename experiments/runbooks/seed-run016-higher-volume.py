import json
from typing import Any

from aipcs_server.config import load_config
from aipcs_server.registry import Registry
from aipcs_server.tools import AipcsTools


def make_tools() -> AipcsTools:
    config = load_config()
    registry = Registry(config.db_path, services_dir=config.services_dir)
    return AipcsTools(registry=registry, owner_id=config.owner_id)


def base_schema(entity_name: str, description: str, domain_fields: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "entities": [
            {
                "name": entity_name,
                "description": description,
                "attributes": [
                    {"name": "id", "type": "uuid", "primary_key": True},
                    {"name": "owner_id", "type": "string", "required": True},
                    *domain_fields,
                    {"name": "created_at", "type": "datetime", "required": True},
                    {"name": "updated_at", "type": "datetime", "required": True},
                    {"name": "created_via", "type": "string", "required": True},
                ],
            }
        ],
        "relationships": [],
        "indices": [
            {"entity": entity_name, "fields": ["owner_id", "topic"]},
            {"entity": entity_name, "fields": ["owner_id", "status"]},
        ],
        "query_patterns": [
            f"list {entity_name} records by topic",
            f"list active {entity_name} records",
        ],
        "migration_history": [],
    }


COMMON_FIELDS = [
    {"name": "record_id", "type": "string", "required": True},
    {"name": "topic", "type": "string", "required": True},
    {"name": "summary", "type": "string", "required": True},
    {"name": "detail", "type": "string"},
    {
        "name": "source_type",
        "type": "string",
        "required": True,
        "allowed_values": [
            "user_stated",
            "codex_admin_seed",
            "agent_observed",
            "agent_inferred",
            "run_summary",
            "operator_note",
        ],
    },
    {"name": "source_label", "type": "string", "required": True},
    {"name": "effective_date", "type": "string", "required": True},
    {
        "name": "status",
        "type": "string",
        "required": True,
        "allowed_values": ["active", "stale", "candidate", "background", "blocked", "superseded"],
    },
    {
        "name": "priority",
        "type": "string",
        "required": True,
        "allowed_values": ["low", "medium", "high"],
    },
]


SERVICES = [
    {
        "domain_name": "research_program",
        "domain_class": "research_planning",
        "intent_description": "Track research direction, evidence needs, and paper-relevant work sequencing.",
        "entity_name": "program_note",
        "entity_description": "A research planning note.",
        "records": [
            {
                "record_id": "RP-001",
                "topic": "next_research_increment",
                "summary": "Small-corpus retrieval and authority reasoning now have positive evidence; the next useful increment should increase memory volume and service overlap.",
                "detail": "The next run should test whether Claude still selects the right context when there are more services and overlapping signals.",
                "source_type": "run_summary",
                "source_label": "post-run015 planning",
                "effective_date": "2026-06-07",
                "status": "active",
                "priority": "high",
            },
            {
                "record_id": "RP-002",
                "topic": "paper_evidence",
                "summary": "The paper needs evidence beyond first-class AIPCS activation and small controlled probes.",
                "detail": "A stronger result would show retrieval discipline under noisier, more realistic memory state.",
                "source_type": "codex_admin_seed",
                "source_label": "experiment class plan",
                "effective_date": "2026-06-07",
                "status": "active",
                "priority": "high",
            },
            {
                "record_id": "RP-003",
                "topic": "comparative_baseline",
                "summary": "Comparative baseline work should wait until the AIPCS higher-volume scenario is stable enough to mirror.",
                "detail": "Agent-memory-v2 comparison matters, but premature comparison risks measuring an unstable AIPCS scenario.",
                "source_type": "codex_admin_seed",
                "source_label": "experiment class plan",
                "effective_date": "2026-06-07",
                "status": "candidate",
                "priority": "medium",
            },
            {
                "record_id": "RP-004",
                "topic": "next_research_increment",
                "summary": "Another explicit authority-conflict probe would be lower value unless the conflict is embedded in larger ordinary context.",
                "detail": "Run015 already tested small explicit authority conflict; a repeat should hide evaluation intent and add corpus pressure.",
                "source_type": "run_summary",
                "source_label": "run015 limitation",
                "effective_date": "2026-06-07",
                "status": "active",
                "priority": "high",
            },
            {
                "record_id": "RP-005",
                "topic": "publication_scope",
                "summary": "Productisation hardening remains important but is not required before the initial paper evidence run sequence.",
                "detail": "Hosting, security, and IT personas should stay in the product roadmap rather than consume research-run time.",
                "source_type": "user_stated",
                "source_label": "paper-readiness discussion",
                "effective_date": "2026-05-21",
                "status": "active",
                "priority": "medium",
            },
        ],
    },
    {
        "domain_name": "experiment_history",
        "domain_class": "experiment_tracking",
        "intent_description": "Track experiment outcomes, caveats, and continuity observations.",
        "entity_name": "history_note",
        "entity_description": "A note about an experiment run or sequence.",
        "records": [
            {
                "record_id": "EH-009-011",
                "topic": "baseline_results",
                "summary": "Runs 009-011 established AIPCS-only recall and small-record discrimination.",
                "detail": "Claude retrieved synthetic records and distinguished applicable, inapplicable, and background data.",
                "source_type": "run_summary",
                "source_label": "runs009-011",
                "effective_date": "2026-06-06",
                "status": "active",
                "priority": "medium",
            },
            {
                "record_id": "EH-012",
                "topic": "autonomous_persistence",
                "summary": "Run012 showed autonomous AIPCS persistence but included auth/model caveats and local file memory behavior.",
                "detail": "Use as behavioral evidence, not as a clean Sonnet-to-Sonnet comparability point.",
                "source_type": "run_summary",
                "source_label": "run012",
                "effective_date": "2026-06-06",
                "status": "active",
                "priority": "medium",
            },
            {
                "record_id": "EH-014",
                "topic": "weak_prompt_activation",
                "summary": "Run014 showed weak-prompt AIPCS activation, but the recommendation drifted toward tool-contract remediation.",
                "detail": "The run was positive for activation and cross-service retrieval, mixed for choosing the most paper-central next step.",
                "source_type": "run_summary",
                "source_label": "run014",
                "effective_date": "2026-06-06",
                "status": "active",
                "priority": "high",
            },
            {
                "record_id": "EH-015",
                "topic": "authority_reasoning",
                "summary": "Run015 passed a small conflicting-authority reasoning test but was partially self-disclosing.",
                "detail": "Claude weighed provenance, recency, status, scope, and cross-validation, but the service description revealed the intended reasoning dimensions.",
                "source_type": "run_summary",
                "source_label": "run015",
                "effective_date": "2026-06-07",
                "status": "active",
                "priority": "high",
            },
            {
                "record_id": "EH-OLD-AUTH",
                "topic": "authority_reasoning",
                "summary": "Authority-conflict testing still needs to be run.",
                "detail": "This note predates run015 and should be treated as stale unless corroborated by newer context.",
                "source_type": "agent_inferred",
                "source_label": "pre-run015 planning",
                "effective_date": "2026-06-06",
                "status": "stale",
                "priority": "low",
            },
        ],
    },
    {
        "domain_name": "lab_operations",
        "domain_class": "operations",
        "intent_description": "Track lab environment constraints, tooling issues, and operational tasks.",
        "entity_name": "ops_note",
        "entity_description": "An operational note for the experiment lab.",
        "records": [
            {
                "record_id": "LO-001",
                "topic": "authentication",
                "summary": "Claude CLI frequently requires authentication during lab runs.",
                "detail": "Record active model after login; treat auth as a caveat unless it changes the answered model or prompt flow.",
                "source_type": "operator_note",
                "source_label": "run014-run015 observations",
                "effective_date": "2026-06-07",
                "status": "active",
                "priority": "medium",
            },
            {
                "record_id": "LO-002",
                "topic": "openwebui",
                "summary": "OpenWebUI/MCP integration remains unresolved and should not displace paper-evidence runs.",
                "detail": "Useful infrastructure later, but not the main blocker for collecting AIPCS evidence.",
                "source_type": "operator_note",
                "source_label": "openwebui detour",
                "effective_date": "2026-06-06",
                "status": "background",
                "priority": "low",
            },
            {
                "record_id": "LO-003",
                "topic": "tool_contract",
                "summary": "AIPCS service design/evolution retries often come from omitted server-managed fields.",
                "detail": "Real implementation friction, but should be separated from research-priority runs unless explicitly testing ergonomics.",
                "source_type": "run_summary",
                "source_label": "runs013-015",
                "effective_date": "2026-06-07",
                "status": "active",
                "priority": "medium",
            },
            {
                "record_id": "LO-004",
                "topic": "archive_quality",
                "summary": "Run artifacts should include terminal transcript, Claude export, seed output, final AIPCS state, and logs.",
                "detail": "This is a process requirement for evidence review, not a research task by itself.",
                "source_type": "operator_note",
                "source_label": "lab runbook",
                "effective_date": "2026-06-06",
                "status": "active",
                "priority": "medium",
            },
        ],
    },
    {
        "domain_name": "memory_findings",
        "domain_class": "agent_behavior",
        "intent_description": "Track observations about agent memory use, retrieval, persistence, and schema behavior.",
        "entity_name": "finding_note",
        "entity_description": "An observation about agent memory behavior.",
        "records": [
            {
                "record_id": "MF-001",
                "topic": "retrieval_behavior",
                "summary": "Claude has repeatedly called AIPCS without explicit memory wording when the task had latent prior-context dependency.",
                "detail": "Evidence includes weak-prompt and planning prompts after AIPCS instructions were available in the harness.",
                "source_type": "run_summary",
                "source_label": "runs009-015",
                "effective_date": "2026-06-07",
                "status": "active",
                "priority": "high",
            },
            {
                "record_id": "MF-002",
                "topic": "authority_reasoning",
                "summary": "Claude can weigh provenance against recency and cross-validation rather than applying a single fixed precedence rule.",
                "detail": "Run015 selected newer convergent planning signals over an older user-stated higher-volume preference.",
                "source_type": "run_summary",
                "source_label": "run015",
                "effective_date": "2026-06-07",
                "status": "active",
                "priority": "high",
            },
            {
                "record_id": "MF-003",
                "topic": "probe_design",
                "summary": "Self-describing services can prime the agent toward the intended reasoning mode.",
                "detail": "Future seeds should use ordinary service descriptions when testing whether reasoning emerges naturally.",
                "source_type": "agent_observed",
                "source_label": "run015 closeout",
                "effective_date": "2026-06-07",
                "status": "active",
                "priority": "high",
            },
            {
                "record_id": "MF-004",
                "topic": "persistence_behavior",
                "summary": "Claude may persist AIPCS outcomes after delegated judgment but usually avoids local file memory when AIPCS is the right durable store.",
                "detail": "Score answer-phase and persistence-phase mutation separately.",
                "source_type": "run_summary",
                "source_label": "runs012-015",
                "effective_date": "2026-06-07",
                "status": "active",
                "priority": "medium",
            },
        ],
    },
    {
        "domain_name": "planning_notes",
        "domain_class": "work_planning",
        "intent_description": "Track work candidates, constraints, and sequencing notes.",
        "entity_name": "work_note",
        "entity_description": "A work-planning note.",
        "records": [
            {
                "record_id": "PN-001",
                "topic": "next_action",
                "summary": "Start agent-memory-v2 comparative wiring next.",
                "detail": "This is important but should follow a stable AIPCS higher-volume scenario so the comparison has a target to mirror.",
                "source_type": "agent_inferred",
                "source_label": "comparison planning",
                "effective_date": "2026-06-07",
                "status": "candidate",
                "priority": "medium",
            },
            {
                "record_id": "PN-002",
                "topic": "next_action",
                "summary": "Run a higher-volume multi-service AIPCS corpus next.",
                "detail": "This is the direct continuation after small-corpus retrieval, schema, weak-prompt, and authority reasoning passes.",
                "source_type": "codex_admin_seed",
                "source_label": "run016 planning",
                "effective_date": "2026-06-07",
                "status": "active",
                "priority": "high",
            },
            {
                "record_id": "PN-003",
                "topic": "next_action",
                "summary": "Fix OpenWebUI integration next.",
                "detail": "Useful if running non-Claude models through OpenWebUI becomes central, but not the strongest immediate paper-evidence move.",
                "source_type": "agent_observed",
                "source_label": "tooling detour",
                "effective_date": "2026-06-06",
                "status": "background",
                "priority": "low",
            },
            {
                "record_id": "PN-004",
                "topic": "next_action",
                "summary": "Backfill the missing run014 record before any new run.",
                "detail": "Could improve continuity, but may also hide a useful continuity-gap signal. It should be decided explicitly, not done automatically.",
                "source_type": "agent_observed",
                "source_label": "run015 closeout",
                "effective_date": "2026-06-07",
                "status": "candidate",
                "priority": "medium",
            },
            {
                "record_id": "PN-005",
                "topic": "next_action",
                "summary": "Repeat run015 with less self-disclosing service descriptions.",
                "detail": "Valuable as a harder authority variant, but higher-volume service overlap can test this while also adding corpus pressure.",
                "source_type": "agent_inferred",
                "source_label": "run015 limitation",
                "effective_date": "2026-06-07",
                "status": "candidate",
                "priority": "medium",
            },
        ],
    },
]


def seed_service(tools: AipcsTools, spec: dict[str, Any]) -> dict[str, Any]:
    seed = tools.aipcs_service_seed(
        domain_name=spec["domain_name"],
        domain_class=spec["domain_class"],
        intent_description=spec["intent_description"],
    )
    service_id = seed["service"]["service_id"]

    if seed.get("duplicate"):
        raise RuntimeError(
            f"Service {spec['domain_name']} already exists in this run. "
            "Reset the run AIPCS state or use a fresh run id before reseeding."
        )

    schema = base_schema(spec["entity_name"], spec["entity_description"], COMMON_FIELDS)
    design = tools.aipcs_service_design(service_id=service_id, schema=schema)
    materialise = tools.aipcs_service_materialise(service_id=service_id)

    created = [
        tools.aipcs_record_create(
            service_id=service_id,
            entity_name=spec["entity_name"],
            record=record,
            created_via="codex_admin_seed",
        )
        for record in spec["records"]
    ]

    return {
        "domain_name": spec["domain_name"],
        "service_id": service_id,
        "entity_name": spec["entity_name"],
        "record_count": len(created),
        "design_accepted": design.get("accepted"),
        "materialised": materialise.get("materialised"),
    }


def main() -> None:
    tools = make_tools()
    seeded = [seed_service(tools, spec) for spec in SERVICES]
    print(
        json.dumps(
            {
                "run": "run016",
                "seed_purpose": "Higher-volume ordinary planning corpus with overlapping services, stale records, and distractors.",
                "service_count": len(seeded),
                "record_count": sum(item["record_count"] for item in seeded),
                "services": seeded,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
