"""Core physics of the rotating-chute burden distribution model.

This is a first-principles engineering *screening* model. It reproduces the
calculation chain of the workbook:

1. Trajectory      - chute exit velocity split + ballistic fall -> landing radius
2. Deposition      - area-weighted Gaussian band per charge, volume-conserving
3. Bed mixing      - volume-weighted voidage with a fines-filling penalty
4. Gas resistance  - two-term Ergun equation -> per-ring relative gas flow

Calibrate against stockline scans, probe temperatures, shaft pressure drop and
burden sampling before any quantitative use.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

from .inputs import Material, Physics, Scenario


# --------------------------------------------------------------------------- #
# Result containers
# --------------------------------------------------------------------------- #
@dataclass
class StepResult:
    """Per-charge trajectory and spread (``Charging_Program`` columns O-Y)."""

    step: int
    material: str
    material_class: str
    active: bool
    mass_t: float
    bulk_density: float
    voidage: float
    dp: float
    v_z0: float = 0.0            # downward exit velocity      (O)
    v_r0: float = 0.0            # radial exit velocity        (P)
    fall_time: float = 0.0       # corrected fall time         (Q)
    v_z_impact: float = 0.0      # downward impact velocity    (R)
    v_impact: float = 0.0        # impact speed                (S)
    ke_specific: float = 0.0     # 0.5 * v_impact^2            (T)
    sigma_base: float = 0.0      # base spread                 (U)
    impact_multiplier: float = 0.0  # broadening factor        (V)
    sigma_eff: float = 0.0       # effective spread            (W)
    landing_radius: float = 0.0  # landing radius              (X)
    denom: float = 0.0           # SUM(shape * area)           (Y)


@dataclass
class RingResult:
    """Per-ring burden and gas state (Radial_Model + Gas_Permeability rows)."""

    ring: int
    r_inner: float
    r_outer: float
    r_mid: float
    area: float
    zone: str = "Mid"

    # Layer thickness contributed by each active step, m
    step_thickness: List[float] = field(default_factory=list)

    coke_thick: float = 0.0
    ore_thick: float = 0.0
    flux_thick: float = 0.0
    total_thick: float = 0.0
    oc_ratio: Optional[float] = None    # ore / coke

    coke_frac: float = 0.0
    ore_frac: float = 0.0
    flux_frac: float = 0.0

    impact_index: float = 0.0           # AA  sum(thick * v_impact^2)/total
    bed_voidage: float = 0.0            # AB  volume-weighted mean voidage
    sauter_dp_all: float = 0.0          # AC
    coke_sauter_dp: float = 0.0         # AD
    oreflux_sauter_dp: float = 0.0      # AE

    # Gas permeability
    size_ratio: float = 1.0             # M
    fines_mix_penalty: float = 0.0      # N
    impact_compact_penalty: float = 0.0  # O
    voidage_mixed: float = 0.0          # P
    ergun_a: float = 0.0                # Q viscous
    ergun_b: float = 0.0                # R inertial @ U_ref
    dp_dl: float = 0.0                  # S pressure gradient Pa/m
    conductance: float = 0.0           # T
    rel_gas_flow: float = 0.0           # U
    flow_vs_uniform: float = 0.0       # V
    interpretation: str = ""            # W
    risk: str = ""                      # X


@dataclass
class Dashboard:
    """Headline KPIs (``Dashboard`` A3:B12)."""

    total_mass: float = 0.0
    coke_mass: float = 0.0
    ore_mass: float = 0.0
    flux_mass: float = 0.0
    avg_landing_over_r: float = 0.0
    max_oc_ratio: float = 0.0
    center_gas_share: float = 0.0
    wall_gas_share: float = 0.0
    max_flow_vs_uniform: float = 0.0
    min_mixed_voidage: float = 0.0


@dataclass
class ModelResult:
    steps: List[StepResult]
    rings: List[RingResult]
    dashboard: Dashboard


# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #
def run_model(scenario: Scenario) -> ModelResult:
    """Run the full model for a scenario and return all computed tables."""
    p = scenario.physics
    materials = scenario.material_map()

    rings = _build_rings(p)
    steps = [_solve_step(s, materials.get(s.material), p) for s in scenario.program]

    _deposit(steps, rings, p)
    _aggregate_rings(steps, rings, p)
    _gas_permeability(rings, p)
    dashboard = _dashboard(scenario, steps, rings, p)

    return ModelResult(steps=steps, rings=rings, dashboard=dashboard)


def _build_rings(p: Physics) -> List[RingResult]:
    rings: List[RingResult] = []
    for i in range(p.n_rings):
        r_inner = i * p.throat_radius / p.n_rings
        r_outer = (i + 1) * p.throat_radius / p.n_rings
        r_mid = 0.5 * (r_inner + r_outer)
        area = math.pi * (r_outer ** 2 - r_inner ** 2)
        if r_mid < 0.25 * p.throat_radius:
            zone = "Center"
        elif r_mid > 0.75 * p.throat_radius:
            zone = "Wall"
        else:
            zone = "Mid"
        rings.append(
            RingResult(ring=i + 1, r_inner=r_inner, r_outer=r_outer,
                       r_mid=r_mid, area=area, zone=zone)
        )
    return rings


def _solve_step(s, mat: Optional[Material], p: Physics) -> StepResult:
    """Trajectory + spread for one charge (Charging_Program O:Y, except Y)."""
    if mat is None:
        raise ValueError(f"Step {s.step}: unknown material {s.material!r}")

    res = StepResult(
        step=s.step, material=s.material, material_class=mat.material_class,
        active=s.active, mass_t=s.mass_t, bulk_density=mat.bulk_density,
        voidage=mat.voidage, dp=mat.dp,
    )
    if not s.active:
        return res

    alpha = math.radians(s.alpha_deg)
    res.v_z0 = s.exit_velocity * math.cos(alpha)                       # O
    res.v_r0 = s.exit_velocity * math.sin(alpha)                       # P
    # Quadratic fall time with downward exit velocity (Q)
    res.fall_time = (
        math.sqrt(res.v_z0 ** 2 + 2 * p.gravity * p.drop_height) - res.v_z0
    ) / p.gravity
    res.v_z_impact = res.v_z0 + p.gravity * res.fall_time               # R
    res.v_impact = math.hypot(res.v_r0, res.v_z_impact)                 # S
    res.ke_specific = 0.5 * res.v_impact ** 2                          # T
    res.sigma_base = (
        p.sigma0 + p.k_dp * mat.dp + p.k_v * s.exit_velocity
        + p.k_roll * mat.rolling_factor
    )                                                                  # U
    res.impact_multiplier = 1 + p.c_impact * (res.v_impact / p.v_ref) ** 2  # V
    res.sigma_eff = res.sigma_base * res.impact_multiplier             # W
    res.landing_radius = max(
        0.0,
        min(p.throat_radius,
            p.pivot_offset + p.chute_length * math.sin(alpha)
            + res.v_r0 * res.fall_time),
    )                                                                  # X
    return res


def _gaussian_shape(r_mid: float, landing: float, sigma: float) -> float:
    return math.exp(-((r_mid - landing) ** 2) / (2 * sigma ** 2))


def _deposit(steps: List[StepResult], rings: List[RingResult], p: Physics) -> None:
    """Distribute each charge across rings, conserving charge volume exactly.

    denom (Y) = SUM_rings(shape * area); thickness in a ring =
    charge_volume * shape / denom.
    """
    for step in steps:
        contributes = (
            step.active and step.mass_t != 0 and step.sigma_eff > 0
        )
        if contributes:
            denom = sum(
                _gaussian_shape(ring.r_mid, step.landing_radius, step.sigma_eff)
                * ring.area
                for ring in rings
            )
        else:
            denom = 0.0
        step.denom = denom

        charge_volume = (
            step.mass_t * 1000.0 / step.bulk_density if contributes else 0.0
        )
        for ring in rings:
            if denom > 0:
                shape = _gaussian_shape(ring.r_mid, step.landing_radius,
                                        step.sigma_eff)
                thickness = charge_volume * shape / denom
            else:
                thickness = 0.0
            ring.step_thickness.append(thickness)


def _aggregate_rings(steps: List[StepResult], rings: List[RingResult],
                     p: Physics) -> None:
    """Roll per-step thickness up into per-ring burden properties."""
    for ring in rings:
        coke = ore = flux = 0.0
        for step, t in zip(steps, ring.step_thickness):
            if step.material_class == "Coke":
                coke += t
            elif step.material_class == "Ore-bearing":
                ore += t
            elif step.material_class == "Flux":
                flux += t
        ring.coke_thick = coke
        ring.ore_thick = ore
        ring.flux_thick = flux
        total = coke + ore + flux
        ring.total_thick = total
        ring.oc_ratio = (ore / coke) if coke > 0 else None

        if total > 0:
            ring.coke_frac = coke / total
            ring.ore_frac = ore / total
            ring.flux_frac = flux / total
            # AA: impact index (mean-square impact velocity, thickness weighted)
            ring.impact_index = sum(
                t * (s.v_impact ** 2 if s.active else 0.0)
                for s, t in zip(steps, ring.step_thickness)
            ) / total
            # AB: volume-weighted mean voidage
            ring.bed_voidage = sum(
                t * s.voidage for s, t in zip(steps, ring.step_thickness)
            ) / total
            # AC: Sauter (surface-area) mean particle size of all material
            inv = sum(
                t / s.dp for s, t in zip(steps, ring.step_thickness) if t
            )
            ring.sauter_dp_all = total / inv if inv else 0.0

        # AD: coke sub-Sauter
        coke_inv = sum(
            t / s.dp for s, t in zip(steps, ring.step_thickness)
            if s.material_class == "Coke" and t
        )
        ring.coke_sauter_dp = coke / coke_inv if coke_inv else 0.0
        # AE: ore+flux sub-Sauter
        of = ore + flux
        of_inv = sum(
            t / s.dp for s, t in zip(steps, ring.step_thickness)
            if s.material_class in ("Ore-bearing", "Flux") and t
        )
        ring.oreflux_sauter_dp = of / of_inv if of_inv else 0.0


def _gas_permeability(rings: List[RingResult], p: Physics) -> None:
    """Two-term Ergun resistance and relative gas flow per ring."""
    for ring in rings:
        voidage_avg = ring.bed_voidage          # K
        dp_eff = ring.sauter_dp_all             # L

        # M: coke/(ore+flux) size disparity, only where both present
        if ring.coke_thick == 0 or (ring.ore_thick + ring.flux_thick) == 0:
            ring.size_ratio = 1.0
        elif ring.oreflux_sauter_dp > 0:
            ring.size_ratio = min(12.0, ring.coke_sauter_dp / ring.oreflux_sauter_dp)
        else:
            ring.size_ratio = 1.0

        # N: fines-filling penalty when coarse coke and finer ore/flux mix
        ring.fines_mix_penalty = (
            p.beta_mix * ring.coke_frac * (ring.ore_frac + ring.flux_frac)
            * (math.log(ring.size_ratio + 1) ** p.gamma_mix)
        )
        # O: impact compaction penalty
        ring.impact_compact_penalty = (
            p.c_compact * (ring.impact_index / (p.v_ref ** 2))
        )
        # P: mixed-bed voidage, floored at eps_min
        ring.voidage_mixed = max(
            p.eps_min,
            voidage_avg - ring.fines_mix_penalty - ring.impact_compact_penalty,
        )

        eps = ring.voidage_mixed
        if not (0 < eps < 1) or dp_eff <= 0:
            ring.ergun_a = ring.ergun_b = ring.dp_dl = ring.conductance = 0.0
            continue
        # Q viscous, R inertial (one U_ref folded in), S = (Q+R)*U_ref
        ring.ergun_a = 150 * p.mu_g * (1 - eps) ** 2 / (eps ** 3 * dp_eff ** 2)
        ring.ergun_b = 1.75 * p.rho_g * p.u_ref * (1 - eps) / (eps ** 3 * dp_eff)
        ring.dp_dl = (ring.ergun_a + ring.ergun_b) * p.u_ref
        ring.conductance = 1.0 / ring.dp_dl if ring.dp_dl else 0.0

    # U: area-weighted, normalised relative gas flow
    sum_cond_area = sum(r.conductance * r.area for r in rings)
    total_area = sum(r.area for r in rings)
    for ring in rings:
        if sum_cond_area > 0:
            ring.rel_gas_flow = ring.conductance * ring.area / sum_cond_area
        else:
            ring.rel_gas_flow = 0.0
        # V: flow relative to a perfectly uniform (area-proportional) flow
        uniform = ring.area / total_area if total_area else 0.0
        ring.flow_vs_uniform = ring.rel_gas_flow / uniform if uniform else 0.0

        v = ring.flow_vs_uniform
        if v > 1.25:
            ring.interpretation = "High gas bias"
        elif v < 0.75:
            ring.interpretation = "Low gas bias"
        else:
            ring.interpretation = "Near uniform"

        if v > p.channel_threshold:
            ring.risk = "Channeling risk"
        elif v < p.low_flow_threshold:
            ring.risk = "Dead/low permeability risk"
        elif ring.fines_mix_penalty > 0.04:
            ring.risk = "Mixed-bed voidage risk"
        else:
            ring.risk = "OK"


def _dashboard(scenario: Scenario, steps: List[StepResult],
               rings: List[RingResult], p: Physics) -> Dashboard:
    d = Dashboard()
    active = [s for s in steps if s.active]
    d.total_mass = sum(s.mass_t for s in active)
    d.coke_mass = sum(s.mass_t for s in active if s.material_class == "Coke")
    d.ore_mass = sum(s.mass_t for s in active if s.material_class == "Ore-bearing")
    d.flux_mass = sum(s.mass_t for s in active if s.material_class == "Flux")

    mass_x = sum(s.mass_t * s.landing_radius for s in active)
    if d.total_mass > 0 and p.throat_radius > 0:
        d.avg_landing_over_r = mass_x / (d.total_mass * p.throat_radius)

    oc = [r.oc_ratio for r in rings if r.oc_ratio is not None]
    d.max_oc_ratio = max(oc) if oc else 0.0
    d.center_gas_share = sum(r.rel_gas_flow for r in rings if r.zone == "Center")
    d.wall_gas_share = sum(r.rel_gas_flow for r in rings if r.zone == "Wall")
    d.max_flow_vs_uniform = max((r.flow_vs_uniform for r in rings), default=0.0)
    d.min_mixed_voidage = min((r.voidage_mixed for r in rings), default=0.0)
    return d
