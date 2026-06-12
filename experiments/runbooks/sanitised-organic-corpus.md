# Sanitised Organic Corpus Runbook

This runbook creates a fictional AIPCS corpus from a private organic `.data` directory.

Use it when the experiment needs realistic service/entity shape without exposing raw personal data. The script rebuilds fresh SQLite files from schema and generated row values. It does not copy raw database files into the output.

## Intent

- Preserve the retrieval problem: multiple services, varied entities, record volume, history volume, and schema shape.
- Remove personal data: names, places, accounts, health values, finance values, paths, domains, conversations, and free text are regenerated.
- Keep the raw corpus private. The raw store is evidence for internal development only, not a paper artifact.
- Treat the sanitised output as experiment material, not as proof that the original corpus is anonymous.

## Generate Snapshot

From the `aipcs` repo:

```bash
python3 experiments/runbooks/sanitise-aipcs-corpus.py \
  --source-data /Users/markrandall/GitHub/aipcs-server/.data \
  --output-data /Users/markrandall/GitHub/aipcs/experiments/snapshots/sanitised-organic-v1-data/.data \
  --owner-id lab \
  --force
```

The generated SQLite files are ignored by git. The script writes a non-sensitive manifest at:

```text
experiments/snapshots/sanitised-organic-v1-data/.data/SANITISED_MANIFEST.json
```

The `--owner-id` must match the AIPCS server's `AIPCS_OWNER_ID`. The lab compose stack currently uses `AIPCS_OWNER_ID=lab`. If these do not match, the data can be present on disk while `aipcs_bootstrap` correctly returns zero services because owner-scoped filtering hides the records.

The generated service endpoints are container paths of the form:

```text
sqlite:////data/services/<service_id>/<domain_name>.sqlite
```

This matches the lab compose mount, where the run's `data/aipcs` directory is mounted into the server container at `/data`. Host paths or `endpoint: null` will make record tools fail even when the registry and service databases exist.

## Privacy Smoke Check

Run this after generation. Extend the marker list when new source-specific terms are known.

```bash
python3 - <<'PY'
import pathlib, subprocess
root = pathlib.Path("experiments/snapshots/sanitised-organic-v1-data/.data")
needles = [
    "Mark",
    "markrandall",
    "randall",
    "/Users/",
    "indigo-blocks",
    "192.168.",
    "10.0.20",
    "QNAP",
    "Brandon",
    "brandon",
]
for needle in needles:
    hits = 0
    for db in root.rglob("*.sqlite"):
        out = subprocess.run(["strings", str(db)], text=True, capture_output=True).stdout
        hits += out.lower().count(needle.lower())
    print(f"{needle}: {hits}")
PY
```

Expected result for `sanitised-organic-v1`: all marker counts are `0`.

## SQLite Integrity Check

```bash
python3 - <<'PY'
import glob, pathlib, sqlite3
for db in sorted(glob.glob("experiments/snapshots/sanitised-organic-v1-data/.data/**/*.sqlite", recursive=True)):
    con = sqlite3.connect(db)
    print(pathlib.Path(db).name, con.execute("pragma integrity_check").fetchone()[0])
    con.close()
PY
```

Expected result: every database reports `ok`.

## Use In A Lab Run

Copy the generated `.data` directory into a run before starting the local AIPCS compose stack:

```bash
RUN_ID=run024
BASELINE=baseline-cli-aipcs-slim-bootstrap-v1

export HOME=/home/markrandall
/opt/aipcs-lab/current/ops/create-run.sh "$RUN_ID" "$BASELINE"
rm -rf "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs"
cp -a /home/markrandall/aipcs-lab/repos/aipcs/experiments/snapshots/sanitised-organic-v1-data/.data \
  "/opt/aipcs-lab/runs/$RUN_ID/data/aipcs"
"/opt/aipcs-lab/runs/$RUN_ID/compose/aipcs/up.sh"
/opt/aipcs-lab/current/ops/wait-mcp.sh
"/opt/aipcs-lab/runs/$RUN_ID/enter-run.sh"
```

Before starting the agent, verify the registry owner matches the compose owner. If `sqlite3` is not installed on the host, run this through the server container after `up.sh`:

```bash
docker exec aipcs-lab-server python - <<'PY'
import sqlite3
con = sqlite3.connect("/data/aipcs-registry.sqlite")
print(con.execute("select owner_id, count(*) from services group by owner_id").fetchall())
print(con.execute("select count(*) from services where endpoint is not null").fetchone())
con.close()
PY
```

Expected result for the lab stack:

```text
[('lab', 11)]
(11,)
```

Then capture the terminal with `script` as usual and start the selected agent.

## Known Limits

- The generated corpus is fictional, not formally anonymised.
- The current generator preserves table names and counts but does not preserve every semantic dependency from the raw corpus.
- History tables preserve operation topology but their before/after payloads are synthetic placeholders.
- If the paper needs a publishable dataset, run a separate disclosure review before release.
