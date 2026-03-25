# -*- coding: utf-8 -*-
import argparse
import re
import sys
from pathlib import Path

from ..services.pipeline_service import run_all


def parse_args():
    parser = argparse.ArgumentParser(description="一鍵下載與分析券商進出明細")
    parser.add_argument("stock_code", type=str, help="股票代碼（4位數，例如 2330）")
    parser.add_argument("--retries", type=int, default=5, help="爬蟲最大重試次數（預設 5）")
    parser.add_argument("--outdir", type=Path, default=Path("output"), help="輸出根目錄（預設 output/）")
    parser.add_argument("--fee-discount", type=float, default=0.28, help="手續費折扣（預設 0.28）")
    parser.add_argument("--day-trade-tax", type=float, default=0.0015, help="當沖稅率（預設 0.0015）")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not re.fullmatch(r"\d{4}", args.stock_code):
        print(f"股票代碼格式不正確：{args.stock_code}（應為 4 位數字）")
        return 1

    try:
        run_all(args.stock_code, args.outdir, args.retries, args.fee_discount, args.day_trade_tax)
    except Exception as exc:
        print(f"❌ 發生錯誤：{exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())