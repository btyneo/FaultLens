from datetime import datetime, timedelta
import re


MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"


def extract_absolute_dates(q: str) -> list[datetime]:
    dates = []
    # format 1: 2020-04-18
    for d in re.findall(r"\d{4}-\d{2}-\d{2}", q):
        dates.append(datetime.strptime(d, "%Y-%m-%d"))
    # format 2: april 18 2020 / april 18, 2020
    for month, day, year in re.findall(rf"({MONTHS}) (\d{{1,2}}),? (\d{{4}})", q):
        dates.append(datetime.strptime(f"{month} {day} {year}", "%B %d %Y"))
    return dates


def extract_time_window(question: str) -> dict:
    now = datetime.utcnow()
    q = question.lower()

    # NEW: real dates come first (e.g. "2020-04-18", "april 18, 2020")
    dates = extract_absolute_dates(q)
    if dates:
        start = min(dates)
        end = max(dates) + timedelta(days=1) - timedelta(seconds=1)
        return {
            "start": start.isoformat() + "Z",
            "end": end.isoformat() + "Z",
            "matched_phrase": "absolute date",
        }

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


# CHANGED: names now match Hamza's component graph (data/graph.py)
SUBSYSTEM_KEYWORDS = {
    "compressor": "Compressor",
    "motor": "Compressor",
    "oil": "Compressor",
    "control panel": "Air Control Panel",
    "reservoir": "Air Control Panel",
    "dryer": "Air Dryer",
    "tower": "Air Dryer",
    "moisture": "Air Dryer",
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