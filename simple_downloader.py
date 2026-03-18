#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版股票券商進出明細下載工具
一鍵下載指定股票的券商買賣明細 CSV 檔案
"""

import os
import re
import sys
import ddddocr  # type: ignore

from broker_scraper_core import download_csv_text, save_raw_csv

def download_stock_csv(stock_code):
    """下載股票券商進出明細 CSV"""
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
    print(f"✅ 下載成功！")
    print(f"📄 檔案: {filename}")
    print(f"📂 位置: {os.path.abspath(filename)}")
    return filename

def main():
    """主程式"""
    print("=" * 50)
    print("   台灣證券交易所券商進出明細下載工具")
    print("=" * 50)
    print()
    
    # 取得股票代碼
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]
    else:
        print("常見股票代碼:")
        print("  2317 - 鴻海     2330 - 台積電")
        print("  4958 - 臻鼎-KY  2454 - 聯發科")
        print("  2412 - 中華電   1301 - 台塑")
        print()
        stock_code = input("請輸入股票代碼: ").strip()
    
    # 檢查代碼格式
    if not re.match(r'^\d{4}$', stock_code):
        print(f"❌ 錯誤: '{stock_code}' 不是有效的股票代碼")
        return
    
    # 下載檔案
    try:
        filename = download_stock_csv(stock_code)
        if filename:
            print(f"\n🎉 任務完成！CSV 檔案已下載完成。")
        else:
            print(f"\n❌ 下載失敗，請稍後再試。")
    
    except KeyboardInterrupt:
        print(f"\n\n⏹️ 使用者中斷操作")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main()
