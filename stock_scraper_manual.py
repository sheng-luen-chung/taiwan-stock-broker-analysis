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
import time
import requests
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup
from collections import defaultdict
import argparse

class StockScraperManual:
    def __init__(self):
        """初始化爬蟲"""
        self.session = None
        self.base_url = 'https://bsr.twse.com.tw/bshtm/bsMenu.aspx'
        
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
        
        for attempt in range(max_retries):
            try:
                self.log(f"第 {attempt + 1} 次嘗試...")
                
                # 建立新的 session
                self.session = requests.Session()
                
                # 取得初始頁面
                self.log("正在連接證交所網站...")
                resp = self.session.get(self.base_url, verify=False)
                
                if resp.status_code != 200:
                    self.log(f"網站連線失敗: HTTP {resp.status_code}")
                    continue
                    
                # 解析頁面並準備表單參數
                soup = BeautifulSoup(resp.text, 'lxml')
                nodes = soup.select('input')
                
                params = {}
                for node in nodes:
                    name = node.attrs.get('name', '')
                    
                    # 跳過特定的控制項
                    if name in ('RadioButton_Excd', 'Button_Reset'):
                        continue
                        
                    if 'value' in node.attrs:
                        params[name] = node.attrs['value']
                    else:
                        params[name] = ''
                
                # 取得驗證碼圖片
                captcha_images = soup.select('#Panel_bshtm img')
                if not captcha_images:
                    self.log("找不到驗證碼圖片")
                    continue
                    
                captcha_image = captcha_images[0]['src']
                m = re.search(r'guid=(.+)', captcha_image)
                if m is None:
                    self.log("無法解析驗證碼圖片URL")
                    continue
                
                # 下載驗證碼圖片
                imgpath = f'{m.group(1)}.jpg'
                captcha_url = 'https://bsr.twse.com.tw/bshtm/' + captcha_image
                
                self.log("正在下載驗證碼圖片...")
                img_resp = requests.get(captcha_url, verify=False)
                
                if img_resp.status_code != 200:
                    self.log("驗證碼圖片下載失敗")
                    continue
                    
                with open(imgpath, 'wb') as f:
                    f.write(img_resp.content)
                
                self.log(f"驗證碼圖片已下載: {imgpath}")
                
                # 自動打開圖片（Windows）
                try:
                    subprocess.run(['start', imgpath], shell=True, check=False)
                    self.log("已自動開啟驗證碼圖片，請查看")
                except:
                    self.log("無法自動開啟圖片，請手動開啟查看驗證碼")
                
                # 手動輸入驗證碼
                print("\n" + "="*50)
                print("請查看已開啟的驗證碼圖片")
                print("="*50)
                vcode = input("請輸入驗證碼: ").strip()
                
                if not vcode:
                    self.log("驗證碼不能為空，跳過此次嘗試")
                    # 清理暫存圖片
                    try:
                        os.remove(imgpath)
                    except:
                        pass
                    continue
                
                self.log(f"使用者輸入驗證碼: {vcode}")
                
                # 清理暫存圖片
                try:
                    os.remove(imgpath)
                except:
                    pass
                
                # 設定表單參數
                params['CaptchaControl1'] = vcode
                params['TextBox_Stkno'] = stock_code
                
                # 提交表單
                self.log("正在提交查詢表單...")
                resp = self.session.post(self.base_url, data=params)
                
                if resp.status_code != 200:
                    self.log(f"表單提交失敗: HTTP {resp.status_code}")
                    continue
                
                # 檢查是否有下載連結
                soup = BeautifulSoup(resp.text, 'lxml')
                download_links = soup.select('#HyperLink_DownloadCSV')
                
                if not download_links:
                    self.log("找不到下載連結，可能是驗證碼錯誤")
                    continue
                
                # 下載 CSV 檔案
                download_url = 'https://bsr.twse.com.tw/bshtm/' + download_links[0]['href']
                self.log("正在下載 CSV 檔案...")
                
                csv_resp = self.session.get(download_url)
                if csv_resp.status_code != 200:
                    self.log("CSV 檔案下載失敗")
                    continue
                
                # 儲存 CSV 檔案
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"{stock_code}_爬蟲資料_{current_time}.csv"
                
                with open(csv_filename, 'w', encoding='utf-8') as f:
                    f.write(csv_resp.text)
                
                self.log(f"成功下載！檔案已儲存為: {csv_filename}")
                
                # 簡單分析資料
                self._analyze_data(csv_resp.text, stock_code)
                
                return True, csv_filename, None
                
            except Exception as e:
                self.log(f"第 {attempt + 1} 次嘗試失敗: {str(e)}")
                continue
        
        return False, None, f"所有 {max_retries} 次嘗試均失敗"
    
    def _analyze_data(self, csv_content, stock_code):
        """簡單分析下載的數據"""
        try:
            lines = csv_content.split("\n")[2:]  # 跳過前兩行標題
            
            # 處理資料
            result = []
            for line in lines:
                list_strs = line.split(",,")  # 分割雙欄資料
                for list_str in list_strs:
                    cleaned = list_str.replace("\u3000", "")  # 移除全角空白
                    if cleaned.strip():
                        result.append(cleaned)
            
            # 統計券商數據
            record = []
            for line_data in result:
                data = line_data.split(',')
                if len(data) >= 5:
                    # 清理券商名稱
                    if len(data) > 1:
                        data[1] = re.sub(r'[0-9A-Za-z]+', '', data[1])
                    record.append(data)
            
            # 移除標題行
            if len(record) > 2:
                record = record[2:]
            
            # 統計分析
            broker_stats = defaultdict(lambda: {"買進": 0, "賣出": 0, "次數": 0})
            total_records = 0
            
            for row in record:
                if len(row) >= 5:
                    try:
                        broker = row[1].strip()
                        if broker:
                            buy_vol = float(row[3].replace(',', '')) if row[3].strip() else 0
                            sell_vol = float(row[4].replace(',', '')) if row[4].strip() else 0
                            
                            broker_stats[broker]["買進"] += buy_vol
                            broker_stats[broker]["賣出"] += sell_vol
                            broker_stats[broker]["次數"] += 1
                            total_records += 1
                    except (ValueError, IndexError):
                        continue
            
            self.log(f"=== 資料分析結果 (股票代碼: {stock_code}) ===")
            self.log(f"總交易筆數: {total_records}")
            self.log(f"券商家數: {len(broker_stats)}")
            
            # 計算買賣超並排序
            broker_netbuy = []
            for broker, stats in broker_stats.items():
                net_buy = (stats["買進"] - stats["賣出"]) / 1000  # 轉換為千股
                broker_netbuy.append((broker, net_buy, stats["買進"]/1000, stats["賣出"]/1000))
            
            # 排序：買超在前
            broker_netbuy.sort(key=lambda x: x[1], reverse=True)
            
            self.log("前 10 大買超券商:")
            for i, (broker, net_buy, buy, sell) in enumerate(broker_netbuy[:10]):
                self.log(f"  {i+1:2d}. {broker:<10} 買超: {net_buy:8.0f}張 (買: {buy:8.0f}張, 賣: {sell:8.0f}張)")
            
            if len(broker_netbuy) > 10:
                self.log("前 10 大賣超券商:")
                for i, (broker, net_buy, buy, sell) in enumerate(broker_netbuy[-10:]):
                    self.log(f"  {i+1:2d}. {broker:<10} 賣超: {abs(net_buy):8.0f}張 (買: {buy:8.0f}張, 賣: {sell:8.0f}張)")
            
        except Exception as e:
            self.log(f"資料分析時發生錯誤: {e}")

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
