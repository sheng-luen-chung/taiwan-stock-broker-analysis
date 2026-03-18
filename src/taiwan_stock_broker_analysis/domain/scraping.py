# -*- coding: utf-8 -*-
import re
from collections import defaultdict
from datetime import datetime

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://bsr.twse.com.tw/bshtm/bsMenu.aspx"


def download_csv_text(stock_code, captcha_solver, max_retries=5, logger=None, timeout=30, verify=False):
    if logger is None:
        logger = lambda message: None

    for attempt in range(1, max_retries + 1):
        try:
            logger(f"第 {attempt} 次嘗試...")
            session = requests.Session()

            logger("正在連接證交所網站...")
            response = session.get(BASE_URL, verify=verify, timeout=timeout)
            if response.status_code != 200:
                logger(f"網站連線失敗: HTTP {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "lxml")
            params = _extract_form_params(soup)

            logger("正在下載驗證碼圖片...")
            captcha_bytes = _download_captcha_bytes(session, soup, timeout=timeout, verify=verify)
            if captcha_bytes is None:
                continue

            captcha_code = captcha_solver(captcha_bytes)
            if not captcha_code:
                continue

            params["CaptchaControl1"] = captcha_code
            params["TextBox_Stkno"] = stock_code

            logger("正在提交查詢表單...")
            response = session.post(BASE_URL, data=params, verify=verify, timeout=timeout)
            if response.status_code != 200:
                logger(f"表單提交失敗: HTTP {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "lxml")
            download_links = soup.select("#HyperLink_DownloadCSV")
            if not download_links:
                logger("找不到下載連結，可能是驗證碼錯誤")
                continue

            logger("正在下載 CSV 檔案...")
            download_url = "https://bsr.twse.com.tw/bshtm/" + download_links[0]["href"]
            csv_response = session.get(download_url, verify=verify, timeout=timeout)
            if csv_response.status_code != 200:
                logger("CSV 檔案下載失敗")
                continue

            return True, csv_response.text, None
        except Exception as exc:
            logger(f"第 {attempt} 次嘗試失敗: {exc}")

    return False, None, f"所有 {max_retries} 次嘗試均失敗"


def save_raw_csv(csv_text, stock_code, label="爬蟲資料", encoding="utf-8-sig"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{stock_code}_{label}_{timestamp}.csv"
    with open(filename, "w", encoding=encoding) as file_obj:
        file_obj.write(csv_text)
    return filename


def save_processed_csv(csv_text, stock_code, out_csv=None, encoding="utf-8-sig"):
    if out_csv is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_csv = f"{stock_code}_處理後資料_{timestamp}.csv"

    lines = csv_text.splitlines()
    with open(out_csv, "w", encoding=encoding, newline="") as file_obj:
        file_obj.write(f"股票代碼: {stock_code} - 券商買賣明細\n")
        file_obj.write(f"下載時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for line in lines:
            cleaned = line.replace("\u3000", " ").strip()
            if cleaned:
                file_obj.write(cleaned + "\n")
    return out_csv


def log_broker_summary(csv_text, stock_code, logger):
    try:
        lines = csv_text.split("\n")[2:]
        flattened_lines = []
        for line in lines:
            for segment in line.split(",,"):
                cleaned = segment.replace("\u3000", "")
                if cleaned.strip():
                    flattened_lines.append(cleaned)

        records = []
        for line in flattened_lines:
            fields = line.split(",")
            if len(fields) >= 5:
                fields[1] = re.sub(r"[0-9A-Za-z]+", "", fields[1])
                records.append(fields)

        if len(records) > 2:
            records = records[2:]

        broker_stats = defaultdict(lambda: {"買進": 0, "賣出": 0, "次數": 0})
        total_records = 0
        for row in records:
            if len(row) < 5:
                continue
            try:
                broker = row[1].strip()
                if not broker:
                    continue
                buy_vol = float(row[3].replace(",", "")) if row[3].strip() else 0
                sell_vol = float(row[4].replace(",", "")) if row[4].strip() else 0
                broker_stats[broker]["買進"] += buy_vol
                broker_stats[broker]["賣出"] += sell_vol
                broker_stats[broker]["次數"] += 1
                total_records += 1
            except (ValueError, IndexError):
                continue

        logger(f"=== 資料分析結果 (股票代碼: {stock_code}) ===")
        logger(f"總交易筆數: {total_records}")
        logger(f"券商家數: {len(broker_stats)}")

        broker_netbuy = []
        for broker, stats in broker_stats.items():
            net_buy = (stats["買進"] - stats["賣出"]) / 1000
            broker_netbuy.append((broker, net_buy, stats["買進"] / 1000, stats["賣出"] / 1000))
        broker_netbuy.sort(key=lambda item: item[1], reverse=True)

        logger("前 10 大買超券商:")
        for index, (broker, net_buy, buy, sell) in enumerate(broker_netbuy[:10], start=1):
            logger(f"  {index:2d}. {broker:<10} 買超: {net_buy:8.0f}張 (買: {buy:8.0f}張, 賣: {sell:8.0f}張)")

        if len(broker_netbuy) > 10:
            logger("前 10 大賣超券商:")
            for index, (broker, net_buy, buy, sell) in enumerate(broker_netbuy[-10:], start=1):
                logger(f"  {index:2d}. {broker:<10} 賣超: {abs(net_buy):8.0f}張 (買: {buy:8.0f}張, 賣: {sell:8.0f}張)")
    except Exception as exc:
        logger(f"資料分析時發生錯誤: {exc}")


def _extract_form_params(soup):
    params = {}
    for node in soup.select("input"):
        name = node.attrs.get("name", "")
        if name in ("RadioButton_Excd", "Button_Reset"):
            continue
        params[name] = node.attrs.get("value", "")
    return params


def _download_captcha_bytes(session, soup, timeout, verify):
    captcha_images = soup.select("#Panel_bshtm img")
    if not captcha_images:
        return None

    captcha_image = captcha_images[0]["src"]
    if re.search(r"guid=(.+)", captcha_image) is None:
        return None

    captcha_url = "https://bsr.twse.com.tw/bshtm/" + captcha_image
    response = session.get(captcha_url, verify=verify, timeout=timeout)
    if response.status_code != 200:
        return None
    return response.content

__all__ = [
    "BASE_URL",
    "download_csv_text",
    "log_broker_summary",
    "save_processed_csv",
    "save_raw_csv",
]