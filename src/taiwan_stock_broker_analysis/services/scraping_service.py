# -*- coding: utf-8 -*-
import os
import subprocess
import tempfile
from datetime import datetime

import ddddocr  # type: ignore

from ..domain.scraping import download_csv_text, log_broker_summary, save_processed_csv, save_raw_csv


def timestamped_log(message: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


class AutomaticCaptchaScraper:
    def __init__(self, logger=timestamped_log):
        self.logger = logger
        self.ocr = ddddocr.DdddOcr()

    def download_stock_data(self, stock_code, max_retries=5):
        self.logger(f"開始爬取股票代碼: {stock_code}")

        success, csv_text, error = download_csv_text(
            stock_code,
            self._solve_captcha,
            max_retries=max_retries,
            logger=self.logger,
        )
        if not success:
            return False, None, error

        csv_filename = save_raw_csv(csv_text, stock_code, label="爬蟲資料", encoding="utf-8-sig")
        self.logger(f"成功下載！檔案已儲存為: {csv_filename}")

        processed_filename = save_processed_csv(csv_text, stock_code)
        self.logger(f"處理後資料已儲存為: {processed_filename}")

        log_broker_summary(csv_text, stock_code, self.logger)
        return True, csv_filename, None

    def download_for_pipeline(self, stock_code: str, max_retries: int = 5):
        self.logger(f"爬取 {stock_code}")
        success, csv_text, error = download_csv_text(
            stock_code,
            self._solve_captcha,
            max_retries=max_retries,
            logger=self.logger,
            timeout=30,
            verify=False,
        )
        if not success:
            return False, None, None, error

        raw_csv = save_raw_csv(csv_text, stock_code, label="爬蟲資料", encoding="utf-8-sig")
        self.logger(f"下載完成：{raw_csv}")

        processed_csv = save_processed_csv(csv_text, stock_code)
        self.logger(f"處理後 CSV 已產生：{processed_csv}")
        return True, raw_csv, processed_csv, None

    def _solve_captcha(self, image_bytes):
        captcha_code = self.ocr.classification(image_bytes)
        self.logger(f"OCR 識別結果: {captcha_code}")
        return captcha_code


class ManualCaptchaScraper:
    def __init__(self, logger=timestamped_log):
        self.logger = logger

    def download_stock_data(self, stock_code, max_retries=5):
        self.logger(f"開始爬取股票代碼: {stock_code}")

        success, csv_text, error = download_csv_text(
            stock_code,
            self._prompt_captcha,
            max_retries=max_retries,
            logger=self.logger,
        )
        if not success:
            return False, None, error

        csv_filename = save_raw_csv(csv_text, stock_code, label="爬蟲資料", encoding="utf-8")
        self.logger(f"成功下載！檔案已儲存為: {csv_filename}")

        log_broker_summary(csv_text, stock_code, self.logger)
        return True, csv_filename, None

    def _prompt_captcha(self, image_bytes):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(image_bytes)
            image_path = temp_file.name

        self.logger(f"驗證碼圖片已下載: {image_path}")
        try:
            subprocess.run(["start", image_path], shell=True, check=False)
            self.logger("已自動開啟驗證碼圖片，請查看")
        except Exception:
            self.logger("無法自動開啟圖片，請手動開啟查看驗證碼")

        print("\n" + "=" * 50)
        print("請查看已開啟的驗證碼圖片")
        print("=" * 50)
        captcha_code = input("請輸入驗證碼: ").strip()

        try:
            os.remove(image_path)
        except OSError:
            pass

        if not captcha_code:
            self.logger("驗證碼不能為空，跳過此次嘗試")
            return ""

        self.logger(f"使用者輸入驗證碼: {captcha_code}")
        return captcha_code


def simple_download_stock_csv(stock_code):
    print(f"🔍 開始下載股票 {stock_code} 的券商進出明細...")

    ocr = ddddocr.DdddOcr()

    def solve_captcha(image_bytes):
        captcha_code = ocr.classification(image_bytes)
        print(f"  驗證碼: {captcha_code}")
        return captcha_code

    success, csv_text, _ = download_csv_text(
        stock_code,
        solve_captcha,
        max_retries=5,
        logger=lambda message: print(f"  {message}"),
    )
    if not success:
        print("❌ 所有嘗試均失敗")
        return None

    filename = save_raw_csv(csv_text, stock_code, label="券商明細", encoding="utf-8")
    print("✅ 下載成功！")
    print(f"📄 檔案: {filename}")
    print(f"📂 位置: {os.path.abspath(filename)}")
    return filename