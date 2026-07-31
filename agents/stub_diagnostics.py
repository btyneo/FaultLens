#this code create the stub data 

from agents.interfaces import AnomalyFlag, DiagnosisResult

# this function return a list of fake AnomalyFlag objects(varied sensors, timestamps, severities).
def detect_anomalies(sensor_data) -> list[AnomalyFlag]:
    return [
        AnomalyFlag(sensor="vibration_motor_3", timestamp="2026-07-31T08:12:00Z", severity=0.82),
        AnomalyFlag(sensor="temp_bearing_1", timestamp="2026-07-31T08:13:15Z", severity=0.45),
        AnomalyFlag(sensor="pressure_valve_7", timestamp="2026-07-31T08:14:30Z", severity=0.28),
        AnomalyFlag(sensor="vibration_motor_3", timestamp="2026-07-31T08:15:50Z", severity=0.91),
    ]

# this function return a fake DiagnosisResults and No anomaly if the flags are empty     
def diagnose(flags: list[AnomalyFlag]) -> DiagnosisResult:
    if not flags:
        return DiagnosisResult(subsystem="none", likely_failure="no_anomalies_detected", confidence=0.0)

    return DiagnosisResult(
        subsystem="motor_assembly",
        likely_failure="bearing_wear",
        confidence=0.73,
    )
    
#"Generating" the data happens fresh, every single time someone calls detect_anomalies() or diagnose(). 
#It's not a one-time output you produce and save — it's baked into the function body 
# as a return statement, so it regenerates on demand    