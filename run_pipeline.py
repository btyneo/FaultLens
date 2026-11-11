from agents.router import route
from agents.retrieval import retrieve
from agents.anomaly import detect_anomalies
from agents.diagnose import diagnose
from agents.recommendation import make_recommendation, request_approval


def run_stages(question: str) -> dict:
    """Runs every pipeline stage and returns all results. No printing, no input()."""
    parsed = route(question)
    data = retrieve(parsed["time_window"])

    if data.empty:
        return {"parsed": parsed, "data_shape": data.shape, "flags": [],
                "diagnosis": None, "recommendation": None}

    flags = detect_anomalies(data)
    diagnosis = diagnose(flags)
    recommendation = make_recommendation(diagnosis, flags)

    return {
        "parsed": parsed,
        "data_shape": data.shape,
        "flags": flags,
        "diagnosis": diagnosis,
        "recommendation": recommendation,
    }


def run(question: str):
    """Terminal version: prints each stage and asks for approval with input()."""
    stages = run_stages(question)
    print("Parsed:", stages["parsed"])
    print("Retrieved:", stages["data_shape"])

    if stages["recommendation"] is None:
        print("No sensor data in this window - cannot diagnose.")
        return {"recommendation": None, "approved": False}

    print("Anomalies:", len(stages["flags"]), "flags")
    print("Diagnose:", stages["diagnosis"])

    approved = request_approval(stages["recommendation"])
    print("FINAL: recommendation approved." if approved
          else "REJECTED: recommendation discarded, nothing is final.")
    return {"recommendation": stages["recommendation"], "approved": approved}


if __name__ == "__main__":
    run("Were there any air leaks on April 18, 2020?")