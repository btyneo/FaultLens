from datetime import datetime, timedelta
import re


def extract_time_window(question: str) -> dict:
    now = datetime.utcnow()
    q = question.lower()

    patterns = [
        (r"last (\d+) hours?", lambda m: timedelta(hours=int(m.group(1)))),
        (r"past (\d+) hours?", lambda m: timedelta(hours=int(m.group(1)))),
        (r"last (\d+) days?",  lambda m: timedelta(days=int(m.group(1)))),
        (r"past (\d+) days?",  lambda m: timedelta(days=int(m.group(1)))),
        (r"last week",         lambda m: timedelta(weeks=1)),
        (r"past week",         lambda m: timedelta(weeks=1)),
        (r"today",             lambda m: timedelta(hours=24)),
    ]

    for pattern, delta_fn in patterns:
        match = re.search(pattern, q)
        if match:
            start = now - delta_fn(match)
            return {
                "start": start.isoformat() + "Z",
                "end": now.isoformat() + "Z",
                "matched_phrase": match.group(0),
            }

    # Fallback: no recognizable time phrase found, default to last 24h
    start = now - timedelta(hours=24)
    return {"start": start.isoformat() + "Z", "end": now.isoformat() + "Z", "matched_phrase": None}


SUBSYSTEM_KEYWORDS = {
    "motor": "motor_assembly",
    "bearing": "motor_assembly",
    "vibration": "motor_assembly",
    "valve": "hydraulic_system",
    "pressure": "hydraulic_system",
    "pump": "hydraulic_system",
    "temp": "thermal_system",
    "temperature": "thermal_system",
}


def extract_subsystem(question: str) -> str | None:
    q = question.lower()
    for keyword, subsystem in SUBSYSTEM_KEYWORDS.items():
        if keyword in q:
            return subsystem
    return None


def route(question: str) -> dict:
    return {
        "time_window": extract_time_window(question),
        "subsystem": extract_subsystem(question),
    }