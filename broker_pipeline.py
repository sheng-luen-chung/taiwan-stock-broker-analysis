# -*- coding: utf-8 -*-
from pathlib import Path

from _workspace_bootstrap import ensure_src_on_path

ensure_src_on_path()

from taiwan_stock_broker_analysis.cli.broker_pipeline_cli import main
from taiwan_stock_broker_analysis.services.analysis_service import analyze_existing_csv


def run_pipeline(input_csv: Path, outdir: Path, fee_discount: float, day_trade_tax: float):
    analyze_existing_csv(input_csv, outdir.parent, fee_discount=fee_discount, day_trade_tax=day_trade_tax)

if __name__ == "__main__":
    raise SystemExit(main())
