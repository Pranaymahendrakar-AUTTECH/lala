"""Command-line entry point.

Run the default workbook scenario and print the dashboard + radial table,
optionally exporting CSVs::

    python -m bld_furnace_model
    python -m bld_furnace_model --rings-csv rings.csv --steps-csv steps.csv
"""
from __future__ import annotations

import argparse

from .inputs import default_scenario
from .model import run_model
from .report import format_report, write_rings_csv, write_steps_csv


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="BLD / Rotating Chute blast-furnace screening model."
    )
    parser.add_argument("--rings-csv", help="write the per-ring table to this CSV")
    parser.add_argument("--steps-csv", help="write the per-step table to this CSV")
    args = parser.parse_args(argv)

    result = run_model(default_scenario())
    print(format_report(result))

    if args.rings_csv:
        write_rings_csv(result, args.rings_csv)
        print(f"\nWrote per-ring table to {args.rings_csv}")
    if args.steps_csv:
        write_steps_csv(result, args.steps_csv)
        print(f"Wrote per-step table to {args.steps_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
