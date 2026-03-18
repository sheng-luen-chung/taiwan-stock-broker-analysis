# -*- coding: utf-8 -*-
import os
import re
import sys
import argparse

from ..services.scraping_service import AutomaticCaptchaScraper


def parse_args():
    parser = argparse.ArgumentParser(
        description="台灣證券交易所券商進出明細爬蟲工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  %(prog)s 2317          # 下載鴻海(2317)的券商進出明細
  %(prog)s 4958          # 下載臻鼎-KY(4958)的券商進出明細
  %(prog)s               # 互動式輸入股票代碼
        """,
    )
    parser.add_argument("stock_code", nargs="?", help="股票代碼 (例如: 2317, 4958)")
    parser.add_argument("--retries", type=int, default=5, help="最大重試次數 (預設: 5)")
    return parser.parse_args()


def _resolve_stock_code(stock_code):
    if stock_code:
        return stock_code

    print("=== 台灣證券交易所券商進出明細爬蟲工具 ===")
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
        value = input("請輸入股票代碼: ").strip()
        if value:
            return value
        print("股票代碼不能為空，請重新輸入")


def main() -> int:
    args = parse_args()
    stock_code = _resolve_stock_code(args.stock_code)

    if not re.match(r"^\d{4}$", stock_code):
        print(f"錯誤: 股票代碼格式不正確 '{stock_code}'，應為4位數字")
        return 1

    scraper = AutomaticCaptchaScraper()
    try:
        success, csv_file, error = scraper.download_stock_data(stock_code, args.retries)
        if success:
            print("\n🎉 成功完成！")
            print(f"📄 CSV 檔案: {csv_file}")
            print(f"📂 儲存位置: {os.path.abspath(csv_file)}")
            return 0

        print(f"\n❌ 下載失敗: {error}")
        return 1
    except KeyboardInterrupt:
        print("\n\n⏹️  使用者中斷操作")
        return 1
    except Exception as exc:
        print(f"\n❌ 發生未預期的錯誤: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())