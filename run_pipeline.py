# -*- coding: utf-8 -*-
"""
一鍵：爬券商進出明細 → 產生處理後 CSV → 跑分析輸出
用法：
  python run_pipeline.py 4958
  python run_pipeline.py 2330 --retries 6 --outdir output --fee-discount 0.28 --day-trade-tax 0.0015
"""

import os
import re
import sys
import time
import argparse
import warnings
from datetime import datetime
from collections import deque
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import ddddocr  # type: ignore
import numpy as np
import pandas as pd

# 關閉 requests 驗證相關雜訊（TWSE 站點常見驗證）
warnings.filterwarnings("ignore", category=UserWarning)
requests.packages.urllib3.disable_warnings()  # type: ignore

# ---------- 參數 ----------
FEE_RATE_STD = 0.001425
BRANCH_TOKENS = [
    "台北","臺北","新北","桃園","台中","臺中","台南","臺南","高雄","基隆","新竹","嘉義","台東","臺東","花蓮","宜蘭",
    "內湖","信義","松山","大安","中山","中正","萬華","文山","南港","士林","北投","板橋","三重","新莊","永和","新店","汐止",
    "中和","林口","淡水","蘆洲","三峽","鶯歌","樹林","五股","泰山","八里","蘆竹","龜山","大園","平鎮","中壢","楊梅","龍潭",
    "竹北","竹南","香山","湖口","新豐","竹東","頭份","苗栗","豐原","北屯","西屯","南屯","大里","太平","霧峰","大甲","沙鹿",
    "員林","彰化","斗六","斗南","虎尾","太保","朴子","新營","永康","仁德","岡山","楠梓","左營","鳳山","小港","屏東","羅東",
    "敦南","復興","南京","忠孝","松德","松江","館前","西門","光復","八德","重慶","建國","文心","中港","中華","民族","民權","民生",
]
BRANCH_RE = "(" + "|".join(map(re.escape, BRANCH_TOKENS)) + ").*"

def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# ---------- 爬蟲 + 產生「處理後 CSV」 ----------
class StockScraper:
    base_url = "https://bsr.twse.com.tw/bshtm/bsMenu.aspx"

    def __init__(self):
        self.session = requests.Session()
        self.ocr = ddddocr.DdddOcr()

    def download(self, stock_code: str, max_retries: int = 5):
        """回傳 (成功與否, raw_csv, processed_csv, err)"""
        for attempt in range(1, max_retries + 1):
            try:
                log(f"爬取 {stock_code}（第 {attempt}/{max_retries} 次）")
                r = self.session.get(self.base_url, verify=False, timeout=30)
                if r.status_code != 200:
                    log(f"初始頁錯誤：HTTP {r.status_code}");  continue

                soup = BeautifulSoup(r.text, "lxml")
                params = {}
                for node in soup.select("input"):
                    name = node.attrs.get("name", "")
                    if name in ("RadioButton_Excd", "Button_Reset"):
                        continue
                    params[name] = node.attrs.get("value", "")

                imgs = soup.select("#Panel_bshtm img")
                if not imgs: log("找不到驗證碼圖片");  continue
                m = re.search(r"guid=(.+)", imgs[0]["src"])
                if not m: log("驗證碼 URL 解析失敗");  continue
                cap_url = "https://bsr.twse.com.tw/bshtm/" + imgs[0]["src"]
                img = self.session.get(cap_url, verify=False, timeout=30)
                if img.status_code != 200: log("驗證碼下載失敗");  continue

                vcode = self.ocr.classification(img.content)
                log(f"OCR 識別碼：{vcode}")

                params["CaptchaControl1"] = vcode
                params["TextBox_Stkno"] = stock_code

                r2 = self.session.post(self.base_url, data=params, verify=False, timeout=30)
                if r2.status_code != 200:
                    log(f"表單提交失敗：HTTP {r2.status_code}");  continue

                soup2 = BeautifulSoup(r2.text, "lxml")
                a = soup2.select("#HyperLink_DownloadCSV")
                if not a:
                    log("找不到 CSV 下載連結（可能驗證碼錯誤）");  continue

                down_url = "https://bsr.twse.com.tw/bshtm/" + a[0]["href"]
                csv_resp = self.session.get(down_url, verify=False, timeout=30)
                if csv_resp.status_code != 200:
                    log("CSV 下載失敗");  continue

                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                raw_csv = f"{stock_code}_爬蟲資料_{ts}.csv"
                with open(raw_csv, "w", encoding="utf-8-sig") as f:
                    f.write(csv_resp.text)
                log(f"下載完成：{raw_csv}")

                processed_csv = f"{stock_code}_處理後資料_{ts}.csv"
                self._save_processed_csv(csv_resp.text, processed_csv, stock_code)
                return True, raw_csv, processed_csv, None
            except Exception as e:
                log(f"嘗試失敗：{e}")
        return False, None, None, f"所有 {max_retries} 次嘗試均失敗"

    @staticmethod
    def _save_processed_csv(csv_text: str, out_csv: str, stock_code: str) -> None:
        lines = csv_text.splitlines()
        with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
            f.write(f"股票代碼: {stock_code} - 券商買賣明細\n")
            f.write(f"下載時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for line in lines:
                cleaned = line.replace("\u3000", " ").strip()
                if cleaned:
                    f.write(cleaned + "\n")
        log(f"處理後 CSV 已產生：{out_csv}")

# ---------- 讀檔 & 分析（沿用您 pipeline 的邏輯） ----------
def read_raw_csv(file_path: Path):
    log(f"讀取檔案：{file_path}")
    raw = file_path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "cp950"):
        try:
            content = raw.decode(enc);  break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("無法解析檔案編碼")
    lines = content.splitlines()

    header_row = None
    header_line = None
    for i, line in enumerate(lines):
        if "序號" in line and "券商" in line:
            header_row = i; header_line = line;  break
    if header_row is None:
        raise ValueError("找不到包含『序號』『券商』的標題行")

    # 左右並排？
    if header_line.count("序號") >= 2:
        parts = header_line.split(",,")
        if len(parts) == 2:
            left_cols  = [c.strip() for c in parts[0].split(",")]
            right_cols = [c.strip() for c in parts[1].split(",")]
            all_rows = []
            for line in lines[header_row + 1:]:
                if not line.strip():  continue
                seg = line.split(",,")
                if len(seg) == 2:
                    l = [v.strip() for v in seg[0].split(",")]
                    if len(l) == len(left_cols) and l[0]:  all_rows.append(l)
                    r = [v.strip() for v in seg[1].split(",")]
                    if len(r) == len(right_cols) and r[0]: all_rows.append(r)
            df = pd.DataFrame(all_rows, columns=left_cols)
        else:
            df = pd.read_csv(file_path, skiprows=header_row, encoding="utf-8-sig")
    else:
        df = pd.read_csv(file_path, skiprows=header_row, encoding="utf-8-sig")

    # 清洗與排序
    base = ["序號","券商","價格","買進股數","賣出股數"]
    right = [c + ".1" for c in base]
    left_df  = df[[c for c in base  if c in df.columns]].copy()
    right_df = df[[c for c in right if c in df.columns]].copy()
    if not right_df.empty:
        right_df.columns = base
        flat = pd.concat([left_df, right_df], ignore_index=True)
    else:
        flat = left_df.copy()
    flat = flat[flat["序號"].notna()].copy()
    for c in ["序號","價格","買進股數","賣出股數"]:
        flat[c] = pd.to_numeric(flat[c], errors="coerce")
    flat["券商"] = (flat["券商"].astype(str)
                    .str.replace("\u3000","", regex=False)
                    .str.replace(r"\s+","", regex=True)
                    .str.strip())
    flat = flat.dropna(subset=["序號"]).sort_values(["序號","券商","價格"], ignore_index=True)
    return flat

def normalize_to_mother(bname: str) -> str:
    if not isinstance(bname, str): bname = str(bname)
    name = re.sub(r"^\d{3,4}", "", bname)
    name = re.sub(BRANCH_RE, "", name)
    name = re.sub("(分公司|分行|營業部|營業處)$", "", name)
    return name or bname

def add_mother_column(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["母券商"] = d["券商"].map(normalize_to_mother)
    return d

def group_by_broker(df: pd.DataFrame, by_col: str) -> pd.DataFrame:
    d = df.copy()
    for c in ["價格","買進股數","賣出股數"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["買金額"] = d["價格"] * d["買進股數"]
    d["賣金額"] = d["價格"] * d["賣出股數"]
    g = d.groupby(by_col, dropna=False).agg(
        買股數=("買進股數","sum"),
        賣股數=("賣出股數","sum"),
        買金額=("買金額","sum"),
        賣金額=("賣金額","sum"),
    )
    out = pd.DataFrame({
        "買張": (g["買股數"]/1000).round(0).astype(int),
        "賣張": (g["賣股數"]/1000).round(0).astype(int),
    }, index=g.index)
    out["買賣超"] = out["買張"] - out["賣張"]
    out["均買價"] = np.where(g["買股數"]>0, g["買金額"]/g["買股數"], np.nan).round(2)
    out["均賣價"] = np.where(g["賣股數"]>0, g["賣金額"]/g["賣股數"], np.nan).round(2)
    return out.sort_values(by=["買賣超","買張","賣張"], ascending=[False, False, True])

def avg_method_pnl(df_mother: pd.DataFrame, fee_discount: float, day_trade_tax: float) -> pd.DataFrame:
    d = df_mother.copy()
    for c in ["價格","買進股數","賣出股數"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["買金額"] = d["價格"] * d["買進股數"]
    d["賣金額"] = d["價格"] * d["賣出股數"]
    g = d.groupby("母券商", dropna=False).agg(
        買股數=("買進股數","sum"),
        賣股數=("賣出股數","sum"),
        買金額=("買金額","sum"),
        賣金額=("賣金額","sum"),
    )
    avg_buy = np.where(g["買股數"]>0, g["買金額"]/g["買股數"], np.nan)
    avg_sell = np.where(g["賣股數"]>0, g["賣金額"]/g["賣股數"], np.nan)
    matched  = np.minimum(g["買股數"], g["賣股數"])
    spread   = avg_sell - avg_buy
    gross    = matched * spread
    fee_rate = FEE_RATE_STD * fee_discount
    buy_turnover  = matched * avg_buy
    sell_turnover = matched * avg_sell
    fee_buy  = buy_turnover  * fee_rate
    fee_sell = sell_turnover * fee_rate
    tax      = sell_turnover * day_trade_tax
    net      = gross - fee_buy - fee_sell - tax
    out = pd.DataFrame({
        "母券商": g.index,
        "回轉股數": matched.astype("Int64"),
        "均買價": np.round(avg_buy, 2),
        "均賣價": np.round(avg_sell, 2),
        "價差": np.round(spread, 3),
        "毛利(均價法)": np.round(gross, 0).astype("Int64"),
        "手續費_買": np.round(fee_buy, 0).astype("Int64"),
        "手續費_賣": np.round(fee_sell, 0).astype("Int64"),
        "證交稅": np.round(tax, 0).astype("Int64"),
        "淨損益(均價法)": np.round(net, 0).astype("Int64"),
    }).set_index("母券商").sort_values("淨損益(均價法)", ascending=False)
    return out

def fifo_pnl_with_carry(df_mother: pd.DataFrame, fee_discount: float, day_trade_tax: float) -> pd.DataFrame:
    d = df_mother.copy()
    for c in ["序號","價格","買進股數","賣出股數"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["序號"])
    buy_ev  = d.loc[d["買進股數"]>0, ["序號","母券商","價格","買進股數"]].rename(columns={"買進股數":"數量"})
    buy_ev["方向"] = "B"
    sell_ev = d.loc[d["賣出股數"]>0, ["序號","母券商","價格","賣出股數"]].rename(columns={"賣出股數":"數量"})
    sell_ev["方向"] = "S"
    ev = pd.concat([buy_ev, sell_ev], ignore_index=True).sort_values(["母券商","序號","方向"])
    fee_rate = FEE_RATE_STD * fee_discount

    rows = []
    from collections import deque
    for broker, grp in ev.groupby("母券商", sort=False):
        long_lots, short_lots = deque(), deque()
        realized = fee_sum = tax_sum = 0.0
        matched_shares = 0
        for _, r in grp.sort_values(["序號","方向"]).iterrows():
            side = r["方向"]; qty = int(r["數量"]); px = float(r["價格"])
            if side == "B":
                while qty > 0 and short_lots:
                    sq_qty, sq_px = short_lots[0]
                    m = min(qty, sq_qty)
                    realized += m * (sq_px - px)
                    fee_sum += (m*px)*fee_rate + (m*sq_px)*fee_rate
                    tax_sum += (m*sq_px)*day_trade_tax
                    matched_shares += m
                    qty -= m;  sq_qty -= m
                    if sq_qty == 0: short_lots.popleft()
                    else: short_lots[0] = (sq_qty, sq_px)
                if qty > 0: long_lots.append((qty, px))
            else:
                while qty > 0 and long_lots:
                    lq, lpx = long_lots[0]
                    m = min(qty, lq)
                    realized += m * (px - lpx)
                    fee_sum += (m*lpx)*fee_rate + (m*px)*fee_rate
                    tax_sum += (m*px)*day_trade_tax
                    matched_shares += m
                    qty -= m;  lq -= m
                    if lq == 0: long_lots.popleft()
                    else: long_lots[0] = (lq, lpx)
                if qty > 0: short_lots.append((qty, px))

        rem_long_qty = sum(q for q,_ in long_lots)
        rem_short_qty = sum(q for q,_ in short_lots)
        rem_long_amt = sum(q*p for q,p in long_lots)
        rem_short_amt = sum(q*p for q,p in short_lots)
        rem_long_avg = (rem_long_amt/rem_long_qty) if rem_long_qty>0 else np.nan
        rem_short_avg = (rem_short_amt/rem_short_qty) if rem_short_qty>0 else np.nan
        sub = d[d["母券商"]==broker]
        buy_shares  = int(sub["買進股數"].sum())
        sell_shares = int(sub["賣出股數"].sum())
        buy_amt  = float((sub["價格"]*sub["買進股數"]).sum())
        sell_amt = float((sub["價格"]*sub["賣出股數"]).sum())
        avg_buy  = (buy_amt/buy_shares) if buy_shares>0 else np.nan
        avg_sell = (sell_amt/sell_shares) if sell_shares>0 else np.nan
        net_pos = rem_long_qty - rem_short_qty
        if net_pos > 0:   net_side, net_avg = "多", rem_long_avg
        elif net_pos < 0: net_side, net_avg = "空", rem_short_avg
        else:             net_side, net_avg = "平", np.nan
        rows.append({
            "母券商": broker,
            "回轉股數(FIFO)": matched_shares,
            "回轉張數(FIFO)": int(round(matched_shares/1000)),
            "已實現毛利(FIFO)": realized,
            "手續費合計(FIFO)": fee_sum,
            "證交稅合計(FIFO)": tax_sum,
            "已實現淨損益(FIFO)": realized - fee_sum - tax_sum,
            "買股數(全日)": buy_shares,
            "賣股數(全日)": sell_shares,
            "均買價(全日)": None if np.isnan(avg_buy)  else round(avg_buy, 2),
            "均賣價(全日)": None if np.isnan(avg_sell) else round(avg_sell,2),
            "相抵後_買股數": rem_long_qty,
            "相抵後_買張數": int(round(rem_long_qty/1000)),
            "相抵後_買均價": None if rem_long_qty==0 else round(rem_long_avg,2),
            "相抵後_賣股數": rem_short_qty,
            "相抵後_賣張數": int(round(rem_short_qty/1000)),
            "相抵後_賣均價": None if rem_short_qty==0 else round(rem_short_avg,2),
            "期末淨部位(股)": int(net_pos),
            "期末淨部位方向": net_side,
            "期末部位均價": None if net_side=="平" else round(net_avg,2),
        })
    out = pd.DataFrame(rows).set_index("母券商").copy()
    for c in ["已實現毛利(FIFO)","手續費合計(FIFO)","證交稅合計(FIFO)","已實現淨損益(FIFO)"]:
        out[c] = pd.to_numeric(out[c], errors="coerce").round(0).astype("Int64")
    return out.sort_values("已實現淨損益(FIFO)", ascending=False)

def top10_profit_loss(fifo_df: pd.DataFrame):
    pos = fifo_df[fifo_df["已實現淨損益(FIFO)"] > 0].sort_values("已實現淨損益(FIFO)", ascending=False).head(10)
    neg = fifo_df[fifo_df["已實現淨損益(FIFO)"] < 0].sort_values("已實現淨損益(FIFO)", ascending=True).head(10)
    return pos, neg

def top10_netflow(fifo_df: pd.DataFrame):
    df = fifo_df.copy()
    if "母券商" not in df.columns:
        df = df.reset_index()
    df["買超股數"] = pd.to_numeric(df["買股數(全日)"], errors="coerce") - pd.to_numeric(df["賣股數(全日)"], errors="coerce")
    df["賣超股數"] = -df["買超股數"]
    df["買超張數"] = (df["買超股數"]/1000).round(0).astype("Int64")
    df["賣超張數"] = (df["賣超股數"]/1000).round(0).astype("Int64")
    cols = ["母券商","買股數(全日)","賣股數(全日)","買超股數","買超張數","賣超股數","賣超張數",
            "回轉張數(FIFO)","已實現毛利(FIFO)","手續費合計(FIFO)","證交稅合計(FIFO)","已實現淨損益(FIFO)",
            "期末淨部位(股)","期末淨部位方向","均買價(全日)","均賣價(全日)"]
    top_netbuy  = df[df["買超張數"]>0].sort_values(["買超張數","已實現淨損益(FIFO)"], ascending=[False, False]).head(10)
    top_netsell = df[df["賣超張數"]>0].sort_values(["賣超張數","已實現淨損益(FIFO)"], ascending=[False, True]).head(10)
    return top_netbuy[cols].copy(), top_netsell[cols].copy()

def run_all(stock_code: str, outdir: Path, retries: int, fee_discount: float, day_trade_tax: float):
    # 1) 爬蟲 & 產生處理後 CSV
    ok, raw_csv, processed_csv, err = StockScraper().download(stock_code, max_retries=retries)
    if not ok:
        raise RuntimeError(err)

    # 2) 分析：輸入用「處理後 CSV」
    input_path = Path(processed_csv)
    input_name = input_path.stem
    out_dir = outdir / f"analysis_{input_name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    flat = read_raw_csv(input_path)
    flat.to_csv(out_dir / "step1_flattened.csv", index=False, encoding="utf-8-sig")

    branch_sum = group_by_broker(flat, "券商")
    branch_sum.to_csv(out_dir / "step2_branch_summary.csv", encoding="utf-8-sig")
    branch_sum.to_excel(out_dir / "step2_branch_summary.xlsx")

    with_mother = add_mother_column(flat)
    mother_sum = group_by_broker(with_mother, "母券商")
    mother_sum.to_csv(out_dir / "step3_mother_summary.csv", encoding="utf-8-sig")
    mother_sum.to_excel(out_dir / "step3_mother_summary.xlsx")

    avg_pnl = avg_method_pnl(with_mother, fee_discount=fee_discount, day_trade_tax=day_trade_tax)
    avg_pnl.to_csv(out_dir / "step4_avg_method_pnl.csv", encoding="utf-8-sig")
    avg_pnl.to_excel(out_dir / "step4_avg_method_pnl.xlsx")

    fifo_ext = fifo_pnl_with_carry(with_mother, fee_discount=fee_discount, day_trade_tax=day_trade_tax)
    fifo_ext.to_csv(out_dir / "step5_fifo_with_carry.csv", encoding="utf-8-sig")
    fifo_ext.to_excel(out_dir / "step5_fifo_with_carry.xlsx")

    pos, neg = top10_profit_loss(fifo_ext.reset_index())
    pos.to_csv(out_dir / "step6_top10_profit.csv",  encoding="utf-8-sig", index=False)
    neg.to_csv(out_dir / "step6_top10_loss.csv",    encoding="utf-8-sig", index=False)

    nb, ns = top10_netflow(fifo_ext.reset_index())
    nb.to_csv(out_dir / "step7_top10_netbuy_pnl.csv",  encoding="utf-8-sig", index=False)
    ns.to_csv(out_dir / "step7_top10_netsell_pnl.csv", encoding="utf-8-sig", index=False)
    with pd.ExcelWriter(out_dir / "step7_netbuy_netsell_pnl.xlsx", engine="openpyxl") as w:
        nb.to_excel(w, sheet_name="買超_TOP10",  index=False)
        ns.to_excel(w, sheet_name="賣超_TOP10", index=False)

    log(f"✅ 全流程完成。輸出目錄：{out_dir.resolve()}")

def parse_args():
    p = argparse.ArgumentParser(description="一鍵下載與分析券商進出明細")
    p.add_argument("stock_code", type=str, help="股票代碼（4位數，例如 2330）")
    p.add_argument("--retries", type=int, default=5, help="爬蟲最大重試次數（預設 5）")
    p.add_argument("--outdir",  type=Path, default=Path("output"), help="輸出根目錄（預設 output/）")
    p.add_argument("--fee-discount", type=float, default=0.28,  help="手續費折扣（預設 0.28）")
    p.add_argument("--day-trade-tax", type=float, default=0.0015, help="當沖稅率（預設 0.0015）")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if not re.fullmatch(r"\d{4}", args.stock_code):
        print(f"股票代碼格式不正確：{args.stock_code}（應為 4 位數字）"); sys.exit(1)
    try:
        run_all(args.stock_code, args.outdir, args.retries, args.fee_discount, args.day_trade_tax)
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        sys.exit(1)
