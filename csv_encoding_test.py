#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV 編碼測試工具
測試不同編碼方式在 Excel 中的顯示效果
"""

import csv
from datetime import datetime

def create_test_files():
    """創建不同編碼的測試 CSV 檔案"""
    
    # 測試資料
    test_data = [
        ['券商名稱', '買進股數', '賣出股數', '淨買賣超'],
        ['元大證券', '1000', '500', '+500'],
        ['凱基證券', '800', '1200', '-400'],
        ['富邦證券', '1500', '300', '+1200'],
        ['統一證券', '600', '900', '-300']
    ]
    
    print("🔧 正在創建測試檔案...")
    
    # 1. UTF-8 (無 BOM) - 舊版本
    with open('測試_UTF8_無BOM.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(test_data)
    print("✅ 已創建: 測試_UTF8_無BOM.csv")
    
    # 2. UTF-8 with BOM - Excel 友好版本
    with open('測試_UTF8_有BOM.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(test_data)
    print("✅ 已創建: 測試_UTF8_有BOM.csv")
    
    # 3. Big5 編碼 - 繁體中文傳統編碼
    try:
        with open('測試_Big5編碼.csv', 'w', encoding='big5', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(test_data)
        print("✅ 已創建: 測試_Big5編碼.csv")
    except UnicodeEncodeError:
        print("❌ Big5 編碼失敗（某些字元無法編碼）")
    
    print("\n📋 測試結果說明:")
    print("1. 測試_UTF8_無BOM.csv - 可能在 Excel 中顯示亂碼")
    print("2. 測試_UTF8_有BOM.csv - Excel 應該能正確顯示中文")
    print("3. 測試_Big5編碼.csv - 傳統編碼，Excel 可能需要手動選擇編碼")
    print("\n💡 建議: 用 Excel 分別開啟這三個檔案，比較顯示效果")
    print("   如果 UTF8_有BOM 版本顯示正確，表示修改成功！")

if __name__ == "__main__":
    create_test_files()
    print(f"\n⏰ 測試完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
