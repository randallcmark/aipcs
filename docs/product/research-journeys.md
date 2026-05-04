# Research and Development Journeys

These are the key workflows in this project. Agents should understand and be able to support each one.

---

## Journey 1: Building the reference implementation

**Who:** Agent + Randall Mark  
**Goal:** A working AIPCS sidecar integrated with Application Tracker, demonstrating the full trigger → scaffold → register lifecycle  
**Entry point:** [../architecture/index.md](../architecture/index.md), then Application Tracker's MCP architecture docs  
**Main path:**
1. Design the schema design prompt (elicits domain schema from the agent)
2. Build the AIPCS sidecar (HTTP management API + SQLite + FastAPI scaffolding)
3. Implement the `service_instantiate` MCP tool
4. Implement dynamic MCP tool discovery (new services appear without restart)
5. Integrate OAuth/DCR for consumer access
6. Validate end-to-end: user request → agent schema design → sidecar instantiation → tool registration → agent uses tool in same session
**Important states:** Milestone M004–M008 in BUILD_JOURNAL  
**Failure states:** Schema validation fails, sidecar port conflict, MCP registration rejected, OAuth/DCR handshake fails  
**Validation:** BUILD_JOURNAL §4 notes; see [../agent/validation.md](../agent/validation.md)

---

## Journey 2: Writing a BUILD_JOURNAL entry

**Who:** Agent or Randall  
**Goal:** A new chronological journal entry that captures a decision, observation, milestone, or surprise  
**Entry point:** [../../journal/BUILD_JOURNAL.md](../../journal/BUILD_JOURNAL.md)  
**Main path:**
1. Copy the entry template block
2. Set the type: Decision | Problem | Observation | Milestone | Spec Change | Surprise
3. Write the summary (one sentence)
4. Fill context, detail, decision/problem/observation, alternatives, implications
5. Fill the **Paper notes** field — which section? what does it illustrate?
6. Update the Decision Log or Spec Change Log if applicable
7. Update Open Questions if something is resolved or new ones arise  
**Important rule:** Don't edit past entries — only add new ones  
**Validation:** Scan the Decision Log to confirm the new entry is reflected there

---

## Journey 3: Updating the pattern spec

**Who:** Agent  
**Goal:** Architecture docs reflect a change to the AIPCS pattern design  
**Entry point:** [../architecture/index.md](../architecture/index.md)  
**Main path:**
1. Add a BUILD_JOURNAL entry (type: Spec Change)
2. Update `docs/architecture/index.md` — which decision changed?
3. If significant: create an ADR in `docs/architecture/decisions/` using the template
4. Add a Spec Change Log entry in the BUILD_JOURNAL
5. Check if `paper/outline.md` §3 (The AIPCS Pattern) needs updating  
**Validation:** Architecture docs agree with BUILD_JOURNAL decision log

---

## Journey 4: Capturing paper material

**Who:** Agent or Randall  
**Goal:** A BUILD_JOURNAL observation is promoted to `paper/outline.md`  
**Entry point:** [paper-rules.md](paper-rules.md)  
**Main path:**
1. Identify the relevant BUILD_JOURNAL running notes section (§1–§7)
2. Assess: is this note substantive enough to promote? Is it more than a placeholder?
3. Add or expand the corresponding section in `paper/outline.md`
4. Do not over-write — paper/outline.md is the outline and key points, not the full draft  
**When to do this:** After any journal entry with strong paper notes; after significant milestones

---

## Journey 5: Creating a formal ADR

**Who:** Agent  
**Goal:** A major pattern or architecture decision is recorded formally  
**Entry point:** [../architecture/decisions/template.md](../architecture/decisions/template.md)  
**Main path:**
1. Copy the template as `ADR-NNN-short-title.md` in `docs/architecture/decisions/`
2. Fill all sections: context, decision, consequences, alternatives, validation
3. Reference the BUILD_JOURNAL entry number
4. Update `docs/architecture/index.md` to link to the new ADR  
**When to use:** Changes to trigger model, mechanism, registration model; any new cross-boundary dependency; any security posture change
