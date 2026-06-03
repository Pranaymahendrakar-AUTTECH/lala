"""Input data structures and the default scenario.

These mirror the ``Inputs`` and ``Charging_Program`` sheets of
``BLD_Rotating_Chute_Blast_Furnace_Model.xlsx`` one-to-one. Edit these (or
build your own :class:`Scenario`) the same way you would edit those two
editable sheets in the workbook.

Units: mass in tonnes per charge step, length in m, density kg/m3,
particle size m, gas viscosity Pa.s, pressure gradient Pa/m.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Physics:
    """Geometry, calibration knobs and gas/Ergun parameters (``Inputs`` sheet)."""

    # Geometry / physics
    throat_radius: float = 3.0          # R, m            (Inputs!D4)
    drop_height: float = 2.5            # H, m            (Inputs!D5)
    pivot_offset: float = 0.0           # r0, m           (Inputs!D6)
    chute_length: float = 2.8           # L, m            (Inputs!D7)
    gravity: float = 9.81               # g, m/s^2        (Inputs!D8)
    n_rings: int = 20                   # N_rings         (Inputs!D9)

    # Spread / deposition calibration
    sigma0: float = 0.22                # base spread, m  (Inputs!D10)
    k_dp: float = 1.8                   # m per m         (Inputs!D11)
    k_v: float = 0.035                  # s               (Inputs!D12)
    k_roll: float = 0.1                 # m               (Inputs!D13)
    c_impact: float = 0.08              # impact broaden  (Inputs!D14)

    # Mixed-bed voidage calibration
    beta_mix: float = 0.18              # fines mix beta  (Inputs!D15)
    gamma_mix: float = 0.6              # fines mix gamma (Inputs!D16)
    eps_min: float = 0.24               # min voidage     (Inputs!D17)
    c_compact: float = 0.02             # impact compact  (Inputs!D18)
    v_ref: float = 5.0                  # ref impact vel  (Inputs!D19)
    rho_g: float = 1.2                  # gas density     (Inputs!D20)

    # Gas / Ergun
    mu_g: float = 3e-5                  # gas viscosity   (Inputs!D23)
    u_ref: float = 1.2                  # superficial vel (Inputs!D24)
    channel_threshold: float = 1.5      # flow/uniform    (Inputs!D25)
    low_flow_threshold: float = 0.5     # flow/uniform    (Inputs!D26)


@dataclass
class Material:
    """A row of the material property table (``Inputs`` A28:H35)."""

    name: str
    material_class: str        # "Coke", "Ore-bearing" or "Flux"
    bulk_density: float        # kg/m3
    voidage: float             # -
    dp: float                  # particle size, m
    repose_deg: float          # -
    friction_mu: float         # -
    rolling_factor: float      # -


@dataclass
class ChargeStep:
    """A row of the charging program (``Charging_Program`` A:G)."""

    step: int
    material: str              # must match a Material.name
    mass_t: float              # tonnes
    alpha_deg: float           # chute angle from vertical
    exit_velocity: float       # m/s
    rotations: float           # informational only
    active: bool = True


@dataclass
class Scenario:
    """A complete model run: physics + materials + charging program."""

    physics: Physics = field(default_factory=Physics)
    materials: List[Material] = field(default_factory=list)
    program: List[ChargeStep] = field(default_factory=list)

    def material_map(self) -> Dict[str, Material]:
        return {m.name: m for m in self.materials}


# --------------------------------------------------------------------------- #
# Default scenario - identical to the values shipped in the workbook.
# --------------------------------------------------------------------------- #
DEFAULT_MATERIALS: List[Material] = [
    #          name           class          bulk  void   dp     rep  mu    roll
    Material("Coke",         "Coke",          500, 0.53, 0.040,  36, 0.45, 1.10),
    Material("Nut coke",     "Coke",          550, 0.48, 0.018,  34, 0.42, 0.80),
    Material("Sinter",       "Ore-bearing",  1850, 0.34, 0.012,  38, 0.55, 0.65),
    Material("Pellet",       "Ore-bearing",  2100, 0.36, 0.014,  28, 0.35, 1.20),
    Material("Lump ore",     "Ore-bearing",  1900, 0.35, 0.025,  40, 0.60, 0.70),
    Material("Flux",         "Flux",         1600, 0.40, 0.018,  37, 0.50, 0.65),
    Material("Mixed burden", "Ore-bearing",  1950, 0.34, 0.016,  36, 0.50, 0.85),
]

DEFAULT_PROGRAM: List[ChargeStep] = [
    #          step material        mass alpha exit rot active
    ChargeStep(1,  "Coke",          5,  46, 2.5, 2, True),
    ChargeStep(2,  "Coke",          5,  34, 2.5, 2, True),
    ChargeStep(3,  "Sinter",        18, 44, 2.8, 2, True),
    ChargeStep(4,  "Pellet",        10, 35, 2.8, 2, True),
    ChargeStep(5,  "Lump ore",      6,  28, 2.4, 1, True),
    ChargeStep(6,  "Flux",          2,  42, 2.2, 1, True),
    ChargeStep(7,  "Nut coke",      1,  38, 2.2, 1, True),
    ChargeStep(8,  "Coke",          0,  30, 2.5, 0, False),
    ChargeStep(9,  "Sinter",        0,  40, 2.8, 0, False),
    ChargeStep(10, "Pellet",        0,  32, 2.8, 0, False),
    ChargeStep(11, "Coke",          0,  50, 2.5, 0, False),
    ChargeStep(12, "Mixed burden",  0,  35, 2.6, 0, False),
]


def default_scenario() -> Scenario:
    """Return the scenario shipped with the workbook."""
    return Scenario(
        physics=Physics(),
        materials=list(DEFAULT_MATERIALS),
        program=list(DEFAULT_PROGRAM),
    )
