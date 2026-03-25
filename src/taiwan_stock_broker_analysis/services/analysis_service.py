# -*- coding: utf-8 -*-
from pathlib import Path

from ..domain.analysis import analyze_csv_file


def build_analysis_output_dir(input_csv: Path, output_root: Path) -> Path:
    input_path = Path(input_csv)
    return Path(output_root) / f"analysis_{input_path.stem}"


def analyze_existing_csv(input_csv: Path, output_root: Path, fee_discount: float, day_trade_tax: float) -> Path:
    input_path = Path(input_csv)
    out_dir = build_analysis_output_dir(input_path, output_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    analyze_csv_file(input_path, out_dir, fee_discount=fee_discount, day_trade_tax=day_trade_tax)
    return out_dir