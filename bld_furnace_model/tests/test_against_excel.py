"""Validate the Python model against ground-truth values read from the workbook.

All expected numbers below were taken directly from the computed cells of
``BLD_Rotating_Chute_Blast_Furnace_Model.xlsx`` for the default scenario, so
this test pins the port to the spreadsheet.
"""
import math

import pytest

from bld_furnace_model import default_scenario, run_model

REL = 1e-6


@pytest.fixture(scope="module")
def result():
    return run_model(default_scenario())


def test_step1_trajectory(result):
    s = result.steps[0]               # Step 1: Coke, 5 t, alpha 46, exit 2.5
    assert s.v_z0 == pytest.approx(1.73664592614749, rel=REL)
    assert s.v_r0 == pytest.approx(1.79834950084663, rel=REL)
    assert s.fall_time == pytest.approx(0.558514498304652, rel=REL)
    assert s.v_z_impact == pytest.approx(7.21567315451613, rel=REL)
    assert s.v_impact == pytest.approx(7.43639697703128, rel=REL)
    assert s.sigma_base == pytest.approx(0.4895, rel=REL)
    assert s.impact_multiplier == pytest.approx(1.17696, rel=REL)
    assert s.sigma_eff == pytest.approx(0.57612192, rel=REL)
    assert s.landing_radius == pytest.approx(3.0, rel=REL)
    assert s.denom == pytest.approx(11.5191249701922, rel=REL)


def test_step2_landing(result):
    s = result.steps[1]               # Step 2: Coke, alpha 34
    assert s.landing_radius == pytest.approx(2.3112190025203, rel=REL)
    assert s.denom == pytest.approx(17.5345724140536, rel=REL)


def test_ring1_burden(result):
    r = result.rings[0]               # r_mid 0.075
    assert r.coke_thick == pytest.approx(0.000307786358965976, rel=1e-5)
    assert r.ore_thick == pytest.approx(0.000234024573306745, rel=1e-5)
    assert r.total_thick == pytest.approx(0.000541819467243483, rel=1e-5)
    assert r.oc_ratio == pytest.approx(0.760347450396964, rel=1e-5)
    assert r.bed_voidage == pytest.approx(0.452690985587212, rel=1e-5)
    assert r.sauter_dp_all == pytest.approx(0.0302982375235496, rel=1e-5)
    assert r.coke_sauter_dp == pytest.approx(0.0399339964223419, rel=1e-5)
    assert r.oreflux_sauter_dp == pytest.approx(0.022999680308513, rel=1e-5)
    assert r.zone == "Center"


def test_ring1_gas(result):
    r = result.rings[0]
    # Dashboard row 4 mirrors Gas_Permeability ring 1
    assert r.voidage_mixed == pytest.approx(0.364200757575523, rel=1e-5)
    assert r.dp_dl == pytest.approx(1362.82018245075, rel=1e-5)
    assert r.flow_vs_uniform == pytest.approx(1.49809141791474, rel=1e-5)


def test_volume_conservation(result):
    """Each active charge's distributed volume must equal its input volume."""
    for j, step in enumerate(result.steps):
        if not step.active or step.mass_t == 0:
            continue
        expected_vol = step.mass_t * 1000.0 / step.bulk_density
        deposited = sum(r.step_thickness[j] * r.area for r in result.rings)
        assert deposited == pytest.approx(expected_vol, rel=1e-9)


def test_dashboard(result):
    d = result.dashboard
    assert d.total_mass == pytest.approx(47.0, rel=REL)
    assert d.coke_mass == pytest.approx(11.0, rel=REL)
    assert d.ore_mass == pytest.approx(34.0, rel=REL)
    assert d.flux_mass == pytest.approx(2.0, rel=REL)
    assert d.avg_landing_over_r == pytest.approx(0.880294660596331, rel=1e-5)
    assert d.max_oc_ratio == pytest.approx(1.06504086784284, rel=1e-5)
    assert d.center_gas_share == pytest.approx(0.0793467182543546, rel=1e-5)
    assert d.wall_gas_share == pytest.approx(0.353140298175314, rel=1e-5)
    assert d.max_flow_vs_uniform == pytest.approx(1.49809141791474, rel=1e-5)
    assert d.min_mixed_voidage == pytest.approx(0.337846706265064, rel=1e-5)


def test_inactive_steps_have_no_thickness(result):
    for j, step in enumerate(result.steps):
        if step.active:
            continue
        assert all(r.step_thickness[j] == 0.0 for r in result.rings)
