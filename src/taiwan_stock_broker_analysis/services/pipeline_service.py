# -*- coding: utf-8 -*-
import warnings
from pathlib import Path

import requests

from .analysis_service import build_analysis_output_dir
from .scraping_service import AutomaticCaptchaScraper, timestamped_log
from ..domain.analysis import analyze_csv_file

warnings.filterwarnings("ignore", category=UserWarning)
requests.packages.urllib3.disable_warnings()  # type: ignore


def run_all(stock_code: str, outdir: Path, retries: int, fee_discount: float, day_trade_tax: float):
    ok, raw_csv, processed_csv, err = AutomaticCaptchaScraper(logger=timestamped_log).download_for_pipeline(
        stock_code,
        max_retries=retries,
    )
    if not ok:
        raise RuntimeError(err)

    input_path = Path(processed_csv)
    out_dir = build_analysis_output_dir(input_path, outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    analyze_csv_file(input_path, out_dir, fee_discount=fee_discount, day_trade_tax=day_trade_tax)
    timestamped_log(f"✅ 全流程完成。輸出目錄：{out_dir.resolve()}")