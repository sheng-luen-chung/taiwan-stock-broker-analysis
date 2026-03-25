# -*- coding: utf-8 -*-
import re
import sys

from ..services.scraping_service import simple_download_stock_csv


def main() -> int:
    print("=" * 50)
    print("   台灣證券交易所券商進出明細下載工具")
    print("=" * 50)
    print()

    if len(sys.argv) > 1:
        stock_code = sys.argv[1]
    else:
        print("常見股票代碼:")
        print("  2317 - 鴻海     2330 - 台積電")
        print("  4958 - 臻鼎-KY  2454 - 聯發科")
        print("  2412 - 中華電   1301 - 台塑")
        print()
        stock_code = input("請輸入股票代碼: ").strip()

    if not re.match(r"^\d{4}$", stock_code):
        print(f"❌ 錯誤: '{stock_code}' 不是有效的股票代碼")
        return 1

    try:
        filename = simple_download_stock_csv(stock_code)
        if filename:
            print("\n🎉 任務完成！CSV 檔案已下載完成。")
            return 0
        print("\n❌ 下載失敗，請稍後再試。")
        return 1
    except KeyboardInterrupt:
        print("\n\n⏹️ 使用者中斷操作")
        return 1
    except Exception as exc:
        print(f"\n❌ 發生錯誤: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())