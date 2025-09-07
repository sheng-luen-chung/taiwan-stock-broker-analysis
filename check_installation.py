#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安裝驗證工具
檢查所有必要套件是否正確安裝
"""

import sys
import importlib
from datetime import datetime

def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 7:
        print("✅ Python 版本符合需求")
        return True
    else:
        print("❌ Python 版本過舊，建議升級至 3.7+")
        return False

def check_package(package_name, import_name=None):
    """檢查單個套件"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        
        # 嘗試取得版本資訊
        version = getattr(module, '__version__', 'unknown')
        
        print(f"✅ {package_name}: {version}")
        return True
        
    except ImportError as e:
        print(f"❌ {package_name}: 未安裝 - {str(e)}")
        return False
    except Exception as e:
        print(f"⚠️  {package_name}: 安裝但可能有問題 - {str(e)}")
        return False

def test_ddddocr():
    """特別測試 ddddocr 初始化"""
    try:
        import ddddocr  # type: ignore
        ocr = ddddocr.DdddOcr()
        print("✅ ddddocr OCR 引擎初始化成功")
        return True
    except Exception as e:
        print(f"❌ ddddocr OCR 引擎初始化失敗: {str(e)}")
        return False

def test_network():
    """測試網路連線"""
    try:
        import requests  # type: ignore
        response = requests.get('https://www.google.com', timeout=5)
        if response.status_code == 200:
            print("✅ 網路連線正常")
            return True
        else:
            print("⚠️  網路連線異常")
            return False
    except Exception as e:
        print(f"❌ 網路連線失敗: {str(e)}")
        return False

def main():
    """主要檢查程序"""
    print("========================================")
    print("   股票爬蟲工具 - 安裝驗證程式")
    print("========================================")
    print(f"檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_good = True
    
    # 檢查 Python 版本
    print("🔍 檢查 Python 版本...")
    if not check_python_version():
        all_good = False
    print()
    
    # 檢查必要套件
    print("🔍 檢查必要套件...")
    required_packages = [
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'),
        ('lxml', 'lxml'),
        ('numpy', 'numpy'),
        ('onnxruntime', 'onnxruntime'),
        ('opencv-python', 'cv2'),
        ('pillow', 'PIL'),
        ('ddddocr', 'ddddocr'),
    ]
    
    for package_name, import_name in required_packages:
        if not check_package(package_name, import_name):
            all_good = False
    
    print()
    
    # 特別測試 ddddocr
    print("🔍 測試 OCR 引擎...")
    if not test_ddddocr():
        all_good = False
    print()
    
    # 測試網路連線
    print("🔍 測試網路連線...")
    if not test_network():
        all_good = False
    print()
    
    # 總結
    print("========================================")
    if all_good:
        print("🎉 所有檢查通過！系統準備就緒")
        print()
        print("現在您可以開始使用股票爬蟲工具：")
        print("  1. 雙擊 快速下載.bat")
        print("  2. 執行 python stock_scraper.py 股票代碼")
        print()
        print("範例: python stock_scraper.py 4958")
    else:
        print("❌ 部分檢查失敗，請查看上方錯誤訊息")
        print()
        print("建議解決方案：")
        print("  1. 查看 INSTALL.md 中的詳細安裝指南")
        print("  2. 執行 install.bat 重新安裝")
        print("  3. 使用虛擬環境避免套件衝突")
    
    print("========================================")
    
    return all_good

if __name__ == "__main__":
    try:
        success = main()
        input("\n按 Enter 鍵退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n使用者中斷檢查")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n檢查過程中發生未預期錯誤: {str(e)}")
        input("按 Enter 鍵退出...")
        sys.exit(1)
