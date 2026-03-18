# -*- coding: utf-8 -*-
import argparse
import sys
from pathlib import Path

from ..services.analysis_service import analyze_existing_csv, build_analysis_output_dir


def parse_args():
    parser = argparse.ArgumentParser(description="券商分點資料處理與 FIFO 撮合全流程")
    parser.add_argument("input", type=str, help="輸入的 CSV 檔案路徑")
    parser.add_argument("--outdir", type=str, default="output", help="輸出資料夾")
    parser.add_argument("--fee_discount", type=float, default=0.28, help="手續費折扣 (預設 0.28)")
    parser.add_argument("--day_trade_tax", type=float, default=0.0015, help="當沖交易稅率 (預設 0.0015)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_root = Path(args.outdir)
    output_dir = build_analysis_output_dir(input_path, output_root)

    print(f"輸入檔案: {args.input}")
    print(f"輸出資料夾: {output_dir}")
    print("=" * 50)

    analyze_existing_csv(input_path, output_root, fee_discount=args.fee_discount, day_trade_tax=args.day_trade_tax)
    return 0


if __name__ == "__main__":
    sys.exit(main())