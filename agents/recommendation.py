# agents/recommendation.py
from agents.interfaces import AnomalyFlag, DiagnosisResult

HIGH_CONF = 0.7
MED_CONF = 0.4


def make_recommendation(diagnosis: DiagnosisResult, flags: list[AnomalyFlag]) -> str:
    # 1. no-anomaly case -> return early
    if not flags or diagnosis.subsystem.lower() == "none":
        return "No anomalies detected in this window. No action needed."

    # 2. readable names (works for "bearing_wear" and "oil leak")
    failure = diagnosis.likely_failure.replace("_", " ")
    subsystem = diagnosis.subsystem.replace("_", " ")

    # 3. unique sensor names, sorted so the output is always in the same order
    sensors = sorted({flag.sensor for flag in flags})
    sensor_text = ", ".join(sensors)

    # 4. wording + action based on confidence
    conf = diagnosis.confidence
    if conf >= HIGH_CONF:
        wording = "likely"
        action = "Recommend inspection within 48 hours."
    elif conf >= MED_CONF:
        wording = "possible"
        action = "Recommend checking at the next scheduled maintenance."
    else:
        wording = "weak signal of"
        action = "No action yet, keep monitoring."

    # 5. one readable sentence
    return (
        f"{sensor_text} flagged ({len(flags)} anomalies) - "
        f"{wording} {failure} in the {subsystem} (confidence {conf:.0%}). {action}"
    )


def request_approval(recommendation: str) -> bool:
    print("\n--- DRAFT RECOMMENDATION ---")
    print(recommendation)
    while True:
        answer = input("Approve? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please type y or n.")