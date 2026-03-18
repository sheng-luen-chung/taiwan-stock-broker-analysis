#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣證券交易所券商進出明細爬蟲工具 (手動驗證碼版本)
自動下載指定股票代碼的券商買賣明細 CSV 檔案

使用方法:
    python stock_scraper_manual.py 2317
    python stock_scraper_manual.py 4958
"""

import os
import re
import sys
import subprocess
import argparse
import tempfile

from broker_scraper_core import download_csv_text, log_broker_summary, save_raw_csv

class StockScraperManual:
    def __init__(self):
        """初始化爬蟲"""
        
    def log(self, message):
        """記錄訊息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def download_stock_data(self, stock_code, max_retries=5):
        """
        下載指定股票代碼的券商進出明細
        
        Args:
            stock_code (str): 股票代碼 (例如: 2317, 4958)
            max_retries (int): 最大重試次數
            
        Returns:
            tuple: (成功標誌, CSV檔案路徑, 錯誤訊息)
        """
        self.log(f"開始爬取股票代碼: {stock_code}")

        success, csv_text, error = download_csv_text(
            stock_code,
            self._prompt_captcha,
            max_retries=max_retries,
            logger=self.log,
        )
        if not success:
            return False, None, error

        csv_filename = save_raw_csv(csv_text, stock_code, label="爬蟲資料", encoding="utf-8")
        self.log(f"成功下載！檔案已儲存為: {csv_filename}")

        log_broker_summary(csv_text, stock_code, self.log)
        return True, csv_filename, None

    def _prompt_captcha(self, image_bytes):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(image_bytes)
            image_path = temp_file.name

        self.log(f"驗證碼圖片已下載: {image_path}")
        try:
            subprocess.run(["start", image_path], shell=True, check=False)
            self.log("已自動開啟驗證碼圖片，請查看")
        except Exception:
            self.log("無法自動開啟圖片，請手動開啟查看驗證碼")

        print("\n" + "=" * 50)
        print("請查看已開啟的驗證碼圖片")
        print("=" * 50)
        captcha_code = input("請輸入驗證碼: ").strip()

        try:
            os.remove(image_path)
        except OSError:
            pass

        if not captcha_code:
            self.log("驗證碼不能為空，跳過此次嘗試")
            return ""

        self.log(f"使用者輸入驗證碼: {captcha_code}")
        return captcha_code

def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='台灣證券交易所券商進出明細爬蟲工具 (手動驗證碼版本)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  %(prog)s 2317          # 下載鴻海(2317)的券商進出明細
  %(prog)s 4958          # 下載臻鼎-KY(4958)的券商進出明細
  %(prog)s               # 互動式輸入股票代碼
        """
    )
    
    parser.add_argument('stock_code', nargs='?', help='股票代碼 (例如: 2317, 4958)')
    parser.add_argument('--retries', type=int, default=5, help='最大重試次數 (預設: 5)')
    
    args = parser.parse_args()
    
    # 取得股票代碼
    if args.stock_code:
        stock_code = args.stock_code
    else:
        print("=== 台灣證券交易所券商進出明細爬蟲工具 (手動驗證碼版本) ===")
        print()
        print("常見股票代碼:")
        print("  2317 - 鴻海")
        print("  2330 - 台積電") 
        print("  4958 - 臻鼎-KY")
        print("  2454 - 聯發科")
        print("  2412 - 中華電")
        print("  1301 - 台塑")
        print()
        
        while True:
            stock_code = input("請輸入股票代碼: ").strip()
            if stock_code:
                break
            print("股票代碼不能為空，請重新輸入")
    
    # 驗證股票代碼格式
    if not re.match(r'^\d{4}$', stock_code):
        print(f"錯誤: 股票代碼格式不正確 '{stock_code}'，應為4位數字")
        sys.exit(1)
    
    # 建立爬蟲並執行
    scraper = StockScraperManual()
    
    try:
        success, csv_file, error = scraper.download_stock_data(stock_code, args.retries)
        
        if success:
            print(f"\n🎉 成功完成！")
            print(f"📄 CSV 檔案: {csv_file}")
            print(f"📂 儲存位置: {os.path.abspath(csv_file)}")
        else:
            print(f"\n❌ 下載失敗: {error}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  使用者中斷操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生未預期的錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
