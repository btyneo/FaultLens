"""
agents/interfaces.py

Shared contract between the data/graph side (Hamza) and the agent pipeline
side (Eya). Both sides import from here.
"""

from dataclasses import dataclass


@dataclass
class AnomalyFlag:
    sensor: str
    timestamp: str
    severity: float


@dataclass
class DiagnosisResult:
    subsystem: str
    likely_failure: str
    confidence: float


def detect_anomalies(sensor_data) -> list[AnomalyFlag]:
    raise NotImplementedError


def diagnose(flags: list[AnomalyFlag]) -> DiagnosisResult:
    raise NotImplementedError