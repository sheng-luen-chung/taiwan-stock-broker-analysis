# -*- coding: utf-8 -*-
"""
一鍵：爬券商進出明細 → 產生處理後 CSV → 跑分析輸出
用法：
  python run_pipeline.py 4958
  python run_pipeline.py 2330 --retries 6 --outdir output --fee-discount 0.28 --day-trade-tax 0.0015
"""

import re
import sys
import argparse
import warnings
from datetime import datetime
from pathlib import Path

import ddddocr  # type: ignore

from broker_analysis_core import analyze_csv_file
from broker_scraper_core import download_csv_text, save_processed_csv, save_raw_csv

# 關閉 requests 驗證相關雜訊（TWSE 站點常見驗證）
warnings.filterwarnings("ignore", category=UserWarning)
requests.packages.urllib3.disable_warnings()  # type: ignore

def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# ---------- 爬蟲 + 產生「處理後 CSV」 ----------
class StockScraper:
    def __init__(self):
        self.ocr = ddddocr.DdddOcr()

    def download(self, stock_code: str, max_retries: int = 5):
        """回傳 (成功與否, raw_csv, processed_csv, err)"""
        log(f"爬取 {stock_code}")
        success, csv_text, error = download_csv_text(
            stock_code,
            self._solve_captcha,
            max_retries=max_retries,
            logger=log,
            timeout=30,
            verify=False,
        )
        if not success:
            return False, None, None, error

        raw_csv = save_raw_csv(csv_text, stock_code, label="爬蟲資料", encoding="utf-8-sig")
        log(f"下載完成：{raw_csv}")

        processed_csv = save_processed_csv(csv_text, stock_code)
        log(f"處理後 CSV 已產生：{processed_csv}")
        return True, raw_csv, processed_csv, None

    def _solve_captcha(self, image_bytes):
        captcha_code = self.ocr.classification(image_bytes)
        log(f"OCR 識別碼：{captcha_code}")
        return captcha_code

def run_all(stock_code: str, outdir: Path, retries: int, fee_discount: float, day_trade_tax: float):
    # 1) 爬蟲 & 產生處理後 CSV
    ok, raw_csv, processed_csv, err = StockScraper().download(stock_code, max_retries=retries)
    if not ok:
        raise RuntimeError(err)

    # 2) 分析：輸入用「處理後 CSV」
    input_path = Path(processed_csv)
    input_name = input_path.stem
    out_dir = outdir / f"analysis_{input_name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    analyze_csv_file(input_path, out_dir, fee_discount=fee_discount, day_trade_tax=day_trade_tax)

    log(f"✅ 全流程完成。輸出目錄：{out_dir.resolve()}")

def parse_args():
    p = argparse.ArgumentParser(description="一鍵下載與分析券商進出明細")
    p.add_argument("stock_code", type=str, help="股票代碼（4位數，例如 2330）")
    p.add_argument("--retries", type=int, default=5, help="爬蟲最大重試次數（預設 5）")
    p.add_argument("--outdir",  type=Path, default=Path("output"), help="輸出根目錄（預設 output/）")
    p.add_argument("--fee-discount", type=float, default=0.28,  help="手續費折扣（預設 0.28）")
    p.add_argument("--day-trade-tax", type=float, default=0.0015, help="當沖稅率（預設 0.0015）")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if not re.fullmatch(r"\d{4}", args.stock_code):
        print(f"股票代碼格式不正確：{args.stock_code}（應為 4 位數字）"); sys.exit(1)
    try:
        run_all(args.stock_code, args.outdir, args.retries, args.fee_discount, args.day_trade_tax)
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        sys.exit(1)
