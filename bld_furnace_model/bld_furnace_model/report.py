"""Human-readable reporting and CSV/Excel export for model results."""
from __future__ import annotations

import csv
from typing import List

from .model import ModelResult, RingResult


RING_COLUMNS = [
    ("ring", "Ring"),
    ("r_mid", "r_mid"),
    ("area", "Area"),
    ("coke_thick", "Coke_thick"),
    ("ore_thick", "Ore_thick"),
    ("flux_thick", "Flux_thick"),
    ("total_thick", "Total_thick"),
    ("oc_ratio", "O/C"),
    ("zone", "Zone"),
    ("bed_voidage", "Voidage_avg"),
    ("sauter_dp_all", "dp_eff_m"),
    ("voidage_mixed", "Voidage_mixed"),
    ("dp_dl", "dP/dL"),
    ("rel_gas_flow", "Rel_gas_flow"),
    ("flow_vs_uniform", "Flow_vs_uniform"),
    ("interpretation", "Interpretation"),
    ("risk", "Risk"),
]


def _fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if value != 0 and (abs(value) < 1e-3 or abs(value) >= 1e5):
            return f"{value:.4e}"
        return f"{value:.4f}"
    return str(value)


def format_dashboard(result: ModelResult) -> str:
    d = result.dashboard
    lines = [
        "BLD / Rotating Chute Model - Dashboard",
        "=" * 44,
        f"  Total charge mass, t        : {d.total_mass:.3f}",
        f"  Total coke-family mass, t   : {d.coke_mass:.3f}",
        f"  Total ore-bearing mass, t   : {d.ore_mass:.3f}",
        f"  Total flux mass, t          : {d.flux_mass:.3f}",
        f"  Avg landing radius / R      : {d.avg_landing_over_r:.4f}",
        f"  Max O/C thickness ratio     : {d.max_oc_ratio:.4f}",
        f"  Center gas share            : {d.center_gas_share:.4f}",
        f"  Wall gas share              : {d.wall_gas_share:.4f}",
        f"  Max flow/uniform            : {d.max_flow_vs_uniform:.4f}",
        f"  Min mixed voidage           : {d.min_mixed_voidage:.4f}",
    ]
    return "\n".join(lines)


def format_ring_table(result: ModelResult) -> str:
    headers = [label for _, label in RING_COLUMNS]
    widths = [max(len(h), 10) for h in headers]
    rows = []
    for ring in result.rings:
        row = [_fmt(getattr(ring, attr)) for attr, _ in RING_COLUMNS]
        rows.append(row)
        widths = [max(w, len(c)) for w, c in zip(widths, row)]

    def line(cells: List[str]) -> str:
        return "  ".join(c.rjust(w) for c, w in zip(cells, widths))

    out = [line(headers), line(["-" * w for w in widths])]
    out.extend(line(r) for r in rows)
    return "\n".join(out)


def format_report(result: ModelResult) -> str:
    return format_dashboard(result) + "\n\n" + format_ring_table(result)


def write_rings_csv(result: ModelResult, path: str) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([label for _, label in RING_COLUMNS])
        for ring in result.rings:
            writer.writerow([getattr(ring, attr) for attr, _ in RING_COLUMNS])


def write_steps_csv(result: ModelResult, path: str) -> None:
    cols = [
        "step", "material", "material_class", "active", "mass_t",
        "v_z0", "v_r0", "fall_time", "v_z_impact", "v_impact",
        "sigma_base", "impact_multiplier", "sigma_eff", "landing_radius",
    ]
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(cols)
        for s in result.steps:
            writer.writerow([getattr(s, c) for c in cols])
