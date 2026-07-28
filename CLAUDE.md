# FaultLens

Agentic diagnostic system over industrial sensor data. Given a plain-English question about equipment sensors, the system routes the query, retrieves the relevant data, detects anomalies, traces them through a component hierarchy graph, and returns a grounded diagnosis with a drafted maintenance recommendation (human-approved before anything is finalized).

## Stack

- Python 3.11, managed via Anaconda (`environment.yml` at repo root)
- LangGraph + LangChain for agent orchestration
- Neo4j for the component hierarchy graph (Engine → Subsystem → Sensor → Failure mode)
- Streamlit for the demo interface
- Dataset: MetroPT (Porto Metro Air Production Unit) — real sensor data, not simulated

## Environment setup

```
conda env create -f environment.yml
conda activate component-health-agent
```

If you add a new package, regenerate the file with:

```
conda env export --from-history > environment.yml
```

(`--from-history` keeps it to what was explicitly installed, not the full transitive dependency tree — commit the updated file.)

## Project structure

- `agents/` — LangGraph pipeline: query router, retrieval agent, anomaly detection agent, graph reasoning agent, recommendation agent
- `data/` — MetroPT ingestion, cleaning, and the component graph schema
- `notebooks/` — exploratory work only; nothing here is part of the final pipeline

## Project structure

This is what the project is supposed to look like at the final stage
, currently it's in production so a lot of file might not be there yet and hamza/Eya will create them

```
faultlens/
├── agents/
│   ├── interfaces.py       # shared contract: AnomalyFlag, DiagnosisResult, detect_anomalies(), diagnose()
│   ├── router.py            # parses the question, picks time window/intent
│   ├── retrieval.py         # pulls the relevant sensor slice
│   ├── anomaly.py            # real detect_anomalies() implementation (Hamza)
│   ├── diagnosis.py          # real diagnose() implementation, uses data/graph.py (Hamza)
│   ├── recommendation.py     # turns DiagnosisResult into drafted text (Eya)
│   └── pipeline.py           # wires all agents together with LangGraph (Eya)
├── data/
│   ├── raw/                  # original MetroPT CSVs — gitignored, not committed
│   ├── ingest.py              # loads + cleans raw CSVs into one DataFrame (Hamza)
│   ├── graph.py                # the component_graph dict: subsystems/sensors/failures (Hamza)
│   └── load.py                  # convenience function: get_sensor_data(time_window) (Hamza)
├── eval/
│   ├── test_cases.py           # the 15-20 labeled Q&A cases + ground truth
│   ├── run_eval.py              # runs pipeline on test cases, computes accuracy
│   └── baseline.py               # naive single-shot LLM comparison
├── demo/
│   └── app.py                    # Streamlit page: pick a window, see the reasoning trace
└── notebooks/                     # exploratory only — never imported by real code
```

**Why split this way**: `agents/` + `data/` mirrors the actual person split — everything under `data/` plus `agents/anomaly.py` and `agents/diagnosis.py` is Hamza's; the rest of `agents/` is Eya's, so the folder itself tells you what's yours. `eval/` is a top-level folder, not buried inside `agents/`, because the ground-truth evaluation is what makes this project credible and should be immediately visible, not an afterthought. `demo/app.py` only ever calls `agents/pipeline.py` — it never reimplements logic — so the demo is provably running the same system that gets evaluated. `data/raw/` and any `*.csv` are gitignored; point to the MetroPT download link in the README instead of committing the data itself. Nothing in `notebooks/` is ever imported by real code — if something built there turns out to matter, it gets promoted into a proper `.py` file.

## Shared interface contract

`agents/interfaces.py` defines the contract between the data/graph side and the agent pipeline side: `AnomalyFlag`, `DiagnosisResult`, `detect_anomalies()`, `diagnose()`. Both branches build against these exact shapes.

- Hamza implements the real versions in `feature/data-graph`.
- Eya implements stub versions with the same shapes (fake but realistic return values) in `feature/agent-pipeline`, so her pipeline is testable before the real logic exists.
- Once Hamza's real versions are merged into `main`, Eya swaps her stub imports for the real ones — no other code should need to change, since the shape stayed identical.
- Don't change the shapes in `interfaces.py` unilaterally — both people depend on them staying stable. Agree together first if a change is genuinely needed.

## Team split

- **Hamza** — dataset ingestion, component graph, anomaly detection agent, evaluation harness. Branch: `feature/data-graph`
- **Eya** — LangGraph orchestration, agent prompts/reasoning, demo interface. Branch: `feature/agent-pipeline`

## Git workflow

- `main` is always working — nobody commits to it directly.
- Work happens on your own feature branch, small commits, pushed regularly.
- Open a Pull Request into `main` when a chunk of work is genuinely done; the other person reviews before merging.
- Link PRs to their GitHub Issue with "Closes #N" so the issue auto-closes on merge.

## Evaluation approach

Ground truth comes from MetroPT's own documented failure events (real, not synthetic) — a small number of real incidents (air leak, oil leak), sliced into multiple test cases plus explicit "nothing's wrong" negative controls, targeting 15-20 labeled cases total. Report diagnosis accuracy and retrieval precision, and always compare against a naive single-shot baseline (raw sensor data into an LLM, no graph, no agent pipeline) — that comparison is the project's core evidence that the structured pipeline does real work.

## Conventions worth knowing

- Sensor-to-module mapping is grounded in MetroPT's own documented sensor descriptions — don't invent mappings; flag any assumption explicitly in code comments if a mapping requires judgment.
- Framing discipline: this is a "multi-agent diagnostic reasoning system," not "a predictive maintenance tutorial" — keep README/demo language leading with the architecture, not the dataset.
