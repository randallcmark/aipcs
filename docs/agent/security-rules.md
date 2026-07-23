# Security Rules

## Core rules

- Don't weaken authentication, authorisation, or input validation
- Don't log tokens, credentials, secrets, or PII — not in journal entries, not in code comments, not in test fixtures
- Validate all input at system boundaries — especially the schema design prompt output, which is agent-generated and must be treated as untrusted input before execution
- The agent-designed schema is a potential injection vector — treat it as untrusted data, validate before executing as SQL or API code
- Persisted memory can become a shadow instruction channel if agents start treating recalled memory as operational policy rather than data — do not let dynamic memory silently outrank system or developer instructions
- Keep secret names in docs, values out of the repo

## OAuth / DCR specific

- The DCR model (OAuth 2.0 Dynamic Client Registration) is a core part of the AIPCS design — don't bypass it in the reference implementation even for convenience
- Client credentials must not appear in any committed file
- The scope model for MCP tools must be explicit — record in BUILD_JOURNAL what each tool scope allows

## Multi-tenant / multi-agent considerations

- AIPCS services are user-scoped — no cross-user data access
- Public v1 resolves same-host, same-effective-user process coordination for
  local SQLite: WAL permits concurrent readers and SQLite serialises one
  writer. Hosted, cross-user, and multi-host coordination remain outside that
  decision and require an explicit design before implementation.
- Keep authority layers explicit: static harness rules, tool contracts, ordinary memory, and any behavior-shaping memory or admin controls must remain distinguishable
- Record any security tradeoff in the BUILD_JOURNAL and update `docs/quality/technical-debt.md`

## Escalation

Ask before:
- Changing the security posture of the OAuth/DCR model
- Accepting a new class of trust (e.g., trusting agent-generated SQL without validation)
- Bypassing scope checks for development convenience

## Review checklist

- Who can access this service or data?
- What data crosses a trust boundary?
- What happens on malformed agent output?
- Could a recalled memory record be mistaken for policy, operator intent, or a higher-order instruction?
- What is logged, and does it contain sensitive data?
- What external systems does this touch?
