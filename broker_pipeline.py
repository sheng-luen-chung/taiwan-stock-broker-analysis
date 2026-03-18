# -*- coding: utf-8 -*-
import argparse
from pathlib import Path

from broker_analysis_core import analyze_csv_file


def run_pipeline(input_csv: Path, outdir: Path, fee_discount: float, day_trade_tax: float):
    analyze_csv_file(input_csv, outdir, fee_discount=fee_discount, day_trade_tax=day_trade_tax)

def parse_args():
    p = argparse.ArgumentParser(description="券商分點資料處理與 FIFO 撮合全流程")
    # 改成必填的位置參數，不要 default
    p.add_argument("input", type=str, help="輸入的 CSV 檔案路徑")
    p.add_argument("--outdir", type=str, default="output", help="輸出資料夾")
    p.add_argument("--fee_discount", type=float, default=0.28, help="手續費折扣 (預設 0.28)")
    p.add_argument("--day_trade_tax", type=float, default=0.0015, help="當沖交易稅率 (預設 0.0015)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # 根據輸入檔案名稱創建專屬的輸出資料夾
    input_name = Path(args.input).stem  # 取得檔名（不含副檔名）
    output_dir = Path(args.outdir) / f"analysis_{input_name}"
    
    print(f"輸入檔案: {args.input}")
    print(f"輸出資料夾: {output_dir}")
    print("=" * 50)
    
    run_pipeline(Path(args.input), output_dir, fee_discount=args.fee_discount, day_trade_tax=args.day_trade_tax)
