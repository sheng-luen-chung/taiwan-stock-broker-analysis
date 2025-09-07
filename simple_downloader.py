#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版股票券商進出明細下載工具
一鍵下載指定股票的券商買賣明細 CSV 檔案
"""

import os
import re
import sys
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import ddddocr  # type: ignore

def download_stock_csv(stock_code):
    """下載股票券商進出明細 CSV"""
    print(f"🔍 開始下載股票 {stock_code} 的券商進出明細...")
    
    # 初始化
    ocr = ddddocr.DdddOcr()
    base_url = 'https://bsr.twse.com.tw/bshtm/bsMenu.aspx'
    
    # 最多重試 5 次
    for attempt in range(5):
        try:
            print(f"  第 {attempt + 1} 次嘗試...")
            
            # 建立 session
            session = requests.Session()
            
            # 取得頁面
            resp = session.get(base_url, verify=False)
            if resp.status_code != 200:
                continue
                
            # 解析表單
            soup = BeautifulSoup(resp.text, 'lxml')
            params = {}
            
            for node in soup.select('input'):
                name = node.attrs.get('name', '')
                if name in ('RadioButton_Excd', 'Button_Reset'):
                    continue
                params[name] = node.attrs.get('value', '')
            
            # 下載驗證碼
            captcha_img = soup.select('#Panel_bshtm img')[0]['src']
            guid = re.search(r'guid=(.+)', captcha_img).group(1)
            
            img_url = f'https://bsr.twse.com.tw/bshtm/{captcha_img}'
            img_resp = requests.get(img_url, verify=False)
            
            # OCR 識別
            vcode = ocr.classification(img_resp.content)
            print(f"  驗證碼: {vcode}")
            
            # 設定參數
            params['CaptchaControl1'] = vcode
            params['TextBox_Stkno'] = stock_code
            
            # 提交表單
            resp = session.post(base_url, data=params)
            if resp.status_code != 200:
                continue
            
            # 找下載連結
            soup = BeautifulSoup(resp.text, 'lxml')
            download_links = soup.select('#HyperLink_DownloadCSV')
            
            if not download_links:
                print("  驗證碼錯誤，重試中...")
                continue
            
            # 下載 CSV
            csv_url = f'https://bsr.twse.com.tw/bshtm/{download_links[0]["href"]}'
            csv_resp = session.get(csv_url)
            
            # 儲存檔案
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{stock_code}_券商明細_{timestamp}.csv"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(csv_resp.text)
            
            print(f"✅ 下載成功！")
            print(f"📄 檔案: {filename}")
            print(f"📂 位置: {os.path.abspath(filename)}")
            
            return filename
            
        except Exception as e:
            print(f"  錯誤: {e}")
            continue
    
    print("❌ 所有嘗試均失敗")
    return None

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
