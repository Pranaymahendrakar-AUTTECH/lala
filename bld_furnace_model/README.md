# BLD / Rotating Chute Blast-Furnace Model

A first-principles engineering **screening** model for burden charging in a
blast furnace fitted with a rotating chute. You define a charging program —
which materials are dumped, in what order, at what chute angle and exit
velocity — and the model predicts:

- **where each charge lands** on the furnace throat,
- **how the burden layers stack up** across 20 concentric radial rings, and
- **how gas flows** up through the resulting bed.

It is a faithful Python port of the workbook
`BLD_Rotating_Chute_Blast_Furnace_Model.xlsx`; the test suite pins every
output to the spreadsheet's computed values.

> ⚠️ This is an engineering screening tool for *comparing* charging cases.
> Calibrate against stockline scans, probe temperatures, shaft pressure drop
> and burden sampling before any quantitative use.

## Install / run

Pure standard library — no third-party runtime dependencies.

```bash
# Run the default scenario (prints dashboard + radial table)
python -m bld_furnace_model

# Export the tables to CSV
python -m bld_furnace_model --rings-csv rings.csv --steps-csv steps.csv

# A worked example incl. a what-if comparison
python examples/run_default.py

# Validate against the spreadsheet's numbers
pip install pytest && pytest
```

Or install it as a package (adds a `bld-furnace` command):

```bash
pip install -e .
bld-furnace
```

## Use it from Python

```python
from bld_furnace_model import default_scenario, run_model
from bld_furnace_model.report import format_report

scenario = default_scenario()           # the workbook's shipped case

# Edit the charging program (the main thing you change):
scenario.program[0].alpha_deg = 52      # throw the first coke charge wallward
scenario.program[2].mass_t = 20         # heavier sinter charge

result = run_model(scenario)
print(format_report(result))

d = result.dashboard
print(d.max_flow_vs_uniform, d.center_gas_share, d.min_mixed_voidage)
```

The two editable structures mirror the editable sheets of the workbook:

- `scenario.physics` — geometry, calibration knobs, gas/Ergun parameters
  (the `Inputs` sheet).
- `scenario.materials` — the material property table.
- `scenario.program` — the list of `ChargeStep`s (the `Charging_Program`
  sheet). Set `active=False` to disable a step.

## The physics chain

| Stage | What it does |
|---|---|
| **Trajectory** | Chute angle α is from vertical, so `v_z0 = v·cos α`, `v_r0 = v·sin α`. Fall time solves `H = v_z0·t + ½g·t²`. Gives each charge a **landing radius**. |
| **Deposition** | Each charge spreads as an **area-weighted Gaussian band** about its landing radius. Ring thickness = `charge_volume · shape / Σ(shape·area)`, which conserves charge volume exactly. |
| **Bed mixing** | Ring voidage is the volume-weighted mean of materials present, reduced by a **fines-filling penalty** where coarse coke and finer ore/flux share a ring, plus an impact-compaction penalty. |
| **Particle size** | The Ergun diameter is the **Sauter (surface-area) mean** per ring; coke and ore/flux sub-means set the size disparity used by the fines penalty. |
| **Gas resistance** | Per-ring pressure gradient from the **two-term Ergun equation** (viscous + inertial). Conductance = 1/(dP/dL); relative gas flow = conductance·area, normalised across rings. |

## Outputs

- **Dashboard KPIs** — total/coke/ore/flux mass, average landing radius / R,
  max O/C thickness ratio, center & wall gas share, max flow-vs-uniform
  (channeling index), and minimum mixed voidage.
- **Per-ring table** — layer thicknesses, O/C ratio, zone, voidage, effective
  particle size, pressure gradient, relative gas flow, and a risk flag
  (`Channeling risk` / `Dead/low permeability risk` / `Mixed-bed voidage
  risk` / `OK`).

## Layout

```
bld_furnace_model/
  inputs.py     # Physics, Material, ChargeStep, Scenario + default scenario
  model.py      # the physics: trajectory, deposition, mixing, Ergun gas flow
  report.py     # text report + CSV export
  cli.py        # `python -m bld_furnace_model`
examples/
  run_default.py
tests/
  test_against_excel.py   # pins outputs to the workbook's computed values
```

## Units

Mass in tonnes per charge step, length in m, density kg/m³, particle size m,
gas viscosity Pa·s, pressure gradient Pa/m. Angles in degrees (from vertical).
