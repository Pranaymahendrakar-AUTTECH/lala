"""Run the default workbook scenario, and a small what-if comparison.

    python examples/run_default.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bld_furnace_model import default_scenario, run_model
from bld_furnace_model.report import format_report


def main() -> None:
    scenario = default_scenario()
    result = run_model(scenario)
    print(format_report(result))

    # What-if: push the first two coke charges further toward the wall by
    # increasing their chute angle, and see how the gas distribution shifts.
    print("\n\n### What-if: coke charges +6 deg chute angle ###")
    for step in scenario.program[:2]:
        step.alpha_deg += 6
    alt = run_model(scenario)
    d0, d1 = result.dashboard, alt.dashboard
    print(f"  Max flow/uniform : {d0.max_flow_vs_uniform:.3f} -> "
          f"{d1.max_flow_vs_uniform:.3f}")
    print(f"  Center gas share : {d0.center_gas_share:.3f} -> "
          f"{d1.center_gas_share:.3f}")
    print(f"  Wall gas share   : {d0.wall_gas_share:.3f} -> "
          f"{d1.wall_gas_share:.3f}")
    print(f"  Min mixed voidage: {d0.min_mixed_voidage:.3f} -> "
          f"{d1.min_mixed_voidage:.3f}")


if __name__ == "__main__":
    main()
