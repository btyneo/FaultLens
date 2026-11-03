from collections import defaultdict
from agents.interfaces import AnomalyFlag, DiagnosisResult
from data.graph import sensor_to_subsystem, component_graph

failure_signatures = {
    "Compressor": {
        "motor overload": ["Motor_current"],
        "oil leak": ["Oil_level", "Oil_temperature"],
        "valve failure": ["DV_eletric", "MPG", "COMP"],
    },
    "Air Control Panel": {
        "air leak": ["TP3", "Reservoirs", "LPS"],
        "pressure regulation failure": ["H1", "Caudal_impulses"],
    },
    "Air Dryer": {
        "moisture carryover": ["DV_pressure"],
        "tower switching failure": ["Towers", "Pressure_switch"],
    },
}


def diagnose(flags: list[AnomalyFlag]) -> DiagnosisResult:
    if not flags:
        return DiagnosisResult(subsystem="None", likely_failure="No anomaly detected", confidence=0.0)

    subsystem_flags = defaultdict(list)
    for flag in flags:
        subsystem = sensor_to_subsystem[flag.sensor]
        subsystem_flags[subsystem].append(flag)

    # root-cause subsystem = earliest flagged sensor, not most flags
    top_subsystem = min(
        subsystem_flags,
        key=lambda s: min(f.timestamp for f in subsystem_flags[s]),
    )
    corroborating_flags = subsystem_flags[top_subsystem]
    flagged_sensors = set(f.sensor for f in corroborating_flags)

    distinct_sensors = len(flagged_sensors)
    total_sensors_in_subsystem = len(component_graph[top_subsystem]["sensors"])
    confidence = min(1.0, distinct_sensors / total_sensors_in_subsystem + 0.3)

    signatures = failure_signatures[top_subsystem]
    scores = {
        mode: len(flagged_sensors & set(sig_sensors))
        for mode, sig_sensors in signatures.items()
    }
    likely_failure = max(scores, key=scores.get)
    if scores[likely_failure] == 0:
        likely_failure = component_graph[top_subsystem]["failure_modes"][0]

    return DiagnosisResult(
        subsystem=top_subsystem,
        likely_failure=likely_failure,
        confidence=round(confidence, 2),
    )