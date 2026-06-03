"""Burden Layer Distribution / Rotating Chute blast-furnace model.

A first-principles engineering screening model that predicts where each charge
lands on the furnace throat, how the burden layers stack up radially, and how
gas flows up through the resulting bed - a Python port of
``BLD_Rotating_Chute_Blast_Furnace_Model.xlsx``.
"""
from .inputs import (
    ChargeStep,
    Material,
    Physics,
    Scenario,
    default_scenario,
    DEFAULT_MATERIALS,
    DEFAULT_PROGRAM,
)
from .model import (
    Dashboard,
    ModelResult,
    RingResult,
    StepResult,
    run_model,
)
from .report import (
    format_dashboard,
    format_report,
    format_ring_table,
    write_rings_csv,
    write_steps_csv,
)

__all__ = [
    "ChargeStep", "Material", "Physics", "Scenario", "default_scenario",
    "DEFAULT_MATERIALS", "DEFAULT_PROGRAM",
    "Dashboard", "ModelResult", "RingResult", "StepResult", "run_model",
    "format_dashboard", "format_report", "format_ring_table",
    "write_rings_csv", "write_steps_csv",
]

__version__ = "1.0.0"
