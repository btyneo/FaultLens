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
