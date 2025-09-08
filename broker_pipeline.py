# -*- coding: utf-8 -*-
import argparse
import math
import re
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd

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

def read_raw_csv(file_path, columns_mapping=None):
    """
    讀取原始 CSV 檔案，處理原始格式
    支援兩種格式：
    1. 標準格式：第一行就是欄位標題  
    2. 註解格式：前面幾行是註解，需要找到包含'序號'和'券商'的標題行
    3. 左右並排格式：一行包含兩組資料
    """
    print(f"正在讀取檔案: {file_path}")
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"檔案不存在: {file_path}")
    
    # 嘗試不同的編碼讀取檔案
    raw_bytes = path.read_bytes()
    for encoding in ['utf-8-sig', 'utf-8', 'cp950']:
        try:
            content = raw_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("無法解析檔案編碼")
    
    lines = content.splitlines()
    print(f"檔案總行數: {len(lines)}")
    
    # 找到包含欄位標題的行
    header_row = None
    header_line = None
    
    for i, line in enumerate(lines):
        # 檢查是否包含標準欄位（序號和券商）
        if '序號' in line and '券商' in line:
            header_row = i
            header_line = line
            print(f"找到標題行於第 {i+1} 行: {line}")
            break
    
    if header_row is None:
        raise ValueError("找不到包含'序號'和'券商'的標題行")
    
    # 檢查是否為左右並排格式（包含兩組序號）
    if header_line.count('序號') >= 2:
        print("偵測到左右並排格式，正在重構資料...")
        
        # 分析標題行來確定欄位分割
        parts = header_line.split(',,')  # 使用雙逗號分割左右兩組
        if len(parts) == 2:
            left_columns = [col.strip() for col in parts[0].split(',')]
            right_columns = [col.strip() for col in parts[1].split(',')]
            print(f"左側欄位: {left_columns}")
            print(f"右側欄位: {right_columns}")
            
            # 重構資料
            all_records = []
            for line in lines[header_row + 1:]:
                if not line.strip():
                    continue
                
                # 分割左右兩組資料
                data_parts = line.split(',,')
                if len(data_parts) == 2:
                    # 處理左側資料
                    left_data = [val.strip() for val in data_parts[0].split(',')]
                    if len(left_data) == len(left_columns) and left_data[0] and left_data[0] != '':
                        all_records.append(left_data)
                    
                    # 處理右側資料  
                    right_data = [val.strip() for val in data_parts[1].split(',')]
                    if len(right_data) == len(right_columns) and right_data[0] and right_data[0] != '':
                        all_records.append(right_data)
            
            # 建立 DataFrame，使用左側的欄位名稱
            df = pd.DataFrame(all_records, columns=left_columns)
        else:
            # 使用 pandas 直接讀取
            df = pd.read_csv(file_path, 
                           skiprows=header_row,
                           encoding='utf-8-sig')
    else:
        # 標準格式，使用 pandas 直接讀取
        df = pd.read_csv(file_path, 
                       skiprows=header_row,
                       encoding='utf-8-sig')
    
    print(f"成功載入資料")
    print(f"欄位名稱: {list(df.columns)}")
    print(f"資料形狀: {df.shape}")
    print(f"前幾行資料:\n{df.head()}")
    
    # 返回 DataFrame 和標題行
    return df, header_line

def flatten_two_groups(df: pd.DataFrame) -> pd.DataFrame:
    base = ["序號","券商","價格","買進股數","賣出股數"]
    right = [c + ".1" for c in base]
    left_df = df[[c for c in base if c in df.columns]].copy()
    right_df = df[[c for c in right if c in df.columns]].copy()
    if not right_df.empty:
        right_df.columns = base
        flat = pd.concat([left_df, right_df], ignore_index=True)
    else:
        flat = left_df.copy()
    flat = flat[flat["序號"].notna()].copy()
    for c in ["序號","價格","買進股數","賣出股數"]:
        flat[c] = pd.to_numeric(flat[c], errors="coerce")
    flat["券商"] = (
        flat["券商"].astype(str)
        .str.replace("\u3000","", regex=False)
        .str.replace(r"\s+","", regex=True)
        .str.strip()
    )
    flat = flat.dropna(subset=["序號"]).sort_values(["序號","券商","價格"], ignore_index=True)
    return flat

def normalize_to_mother(bname: str) -> str:
    if not isinstance(bname, str):
        bname = str(bname)
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
    out = out.sort_values(by=["買賣超","買張","賣張"], ascending=[False, False, True])
    return out

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
    matched = np.minimum(g["買股數"], g["賣股數"])
    spread = avg_sell - avg_buy
    gross = matched * spread
    fee_rate = FEE_RATE_STD * fee_discount
    buy_turnover  = matched * avg_buy
    sell_turnover = matched * avg_sell
    fee_buy  = buy_turnover  * fee_rate
    fee_sell = sell_turnover * fee_rate
    tax = sell_turnover * day_trade_tax
    net = gross - fee_buy - fee_sell - tax
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
    buy_ev = d.loc[d["買進股數"]>0, ["序號","母券商","價格","買進股數"]].rename(columns={"買進股數":"數量"})
    buy_ev["方向"] = "B"
    sell_ev = d.loc[d["賣出股數"]>0, ["序號","母券商","價格","賣出股數"]].rename(columns={"賣出股數":"數量"})
    sell_ev["方向"] = "S"
    ev = pd.concat([buy_ev, sell_ev], ignore_index=True).sort_values(["母券商","序號","方向"])
    fee_rate = FEE_RATE_STD * fee_discount

    rows = []
    for broker, grp in ev.groupby("母券商", sort=False):
        long_lots, short_lots = deque(), deque()
        realized = 0.0
        fee_sum = 0.0
        tax_sum = 0.0
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
                    qty -= m; sq_qty -= m
                    if sq_qty == 0: short_lots.popleft()
                    else: short_lots[0] = (sq_qty, sq_px)
                if qty > 0:
                    long_lots.append((qty, px))
            else:
                while qty > 0 and long_lots:
                    lq, lpx = long_lots[0]
                    m = min(qty, lq)
                    realized += m * (px - lpx)
                    fee_sum += (m*lpx)*fee_rate + (m*px)*fee_rate
                    tax_sum += (m*px)*day_trade_tax
                    matched_shares += m
                    qty -= m; lq -= m
                    if lq == 0: long_lots.popleft()
                    else: long_lots[0] = (lq, lpx)
                if qty > 0:
                    short_lots.append((qty, px))
        rem_long_qty = sum(q for q,_ in long_lots)
        rem_short_qty = sum(q for q,_ in short_lots)
        rem_long_amt = sum(q*p for q,p in long_lots)
        rem_short_amt = sum(q*p for q,p in short_lots)
        rem_long_avg = (rem_long_amt/rem_long_qty) if rem_long_qty>0 else np.nan
        rem_short_avg = (rem_short_amt/rem_short_qty) if rem_short_qty>0 else np.nan
        sub = d[d["母券商"]==broker]
        buy_shares = int(sub["買進股數"].sum())
        sell_shares = int(sub["賣出股數"].sum())
        buy_amt = float((sub["價格"]*sub["買進股數"]).sum())
        sell_amt = float((sub["價格"]*sub["賣出股數"]).sum())
        avg_buy = (buy_amt/buy_shares) if buy_shares>0 else np.nan
        avg_sell = (sell_amt/sell_shares) if sell_shares>0 else np.nan
        net_pos = rem_long_qty - rem_short_qty
        if net_pos > 0:
            net_side = "多"; net_avg = rem_long_avg
        elif net_pos < 0:
            net_side = "空"; net_avg = rem_short_avg
        else:
            net_side = "平"; net_avg = np.nan
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
            "均買價(全日)": None if math.isnan(avg_buy) else round(avg_buy,2),
            "均賣價(全日)": None if math.isnan(avg_sell) else round(avg_sell,2),
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
    cols_out = ["母券商","買股數(全日)","賣股數(全日)","買超股數","買超張數","賣超股數","賣超張數",
                "回轉張數(FIFO)","已實現毛利(FIFO)","手續費合計(FIFO)","證交稅合計(FIFO)","已實現淨損益(FIFO)",
                "期末淨部位(股)","期末淨部位方向","均買價(全日)","均賣價(全日)"]
    top_netbuy = df[df["買超張數"]>0].sort_values(["買超張數","已實現淨損益(FIFO)"], ascending=[False, False]).head(10)
    top_netsell = df[df["賣超張數"]>0].sort_values(["賣超張數","已實現淨損益(FIFO)"], ascending=[False, True]).head(10)
    return top_netbuy[cols_out].copy(), top_netsell[cols_out].copy()

def run_pipeline(input_csv: Path, outdir: Path, fee_discount: float, day_trade_tax: float):
    outdir.mkdir(parents=True, exist_ok=True)
    raw_df, hdr = read_raw_csv(input_csv)
    flat = flatten_two_groups(raw_df)
    flat.to_csv(outdir / "step1_flattened.csv", index=False, encoding="utf-8-sig")
    branch_sum = group_by_broker(flat, "券商")
    branch_sum.to_csv(outdir / "step2_branch_summary.csv", encoding="utf-8-sig")
    branch_sum.to_excel(outdir / "step2_branch_summary.xlsx")
    with_mother = add_mother_column(flat)
    mother_sum = group_by_broker(with_mother, "母券商")
    mother_sum.to_csv(outdir / "step3_mother_summary.csv", encoding="utf-8-sig")
    mother_sum.to_excel(outdir / "step3_mother_summary.xlsx")
    avg_pnl = avg_method_pnl(with_mother, fee_discount=fee_discount, day_trade_tax=day_trade_tax)
    avg_pnl.to_csv(outdir / "step4_avg_method_pnl.csv", encoding="utf-8-sig")
    avg_pnl.to_excel(outdir / "step4_avg_method_pnl.xlsx")
    fifo_ext = fifo_pnl_with_carry(with_mother, fee_discount=fee_discount, day_trade_tax=day_trade_tax)
    fifo_ext.to_csv(outdir / "step5_fifo_with_carry.csv", encoding="utf-8-sig")
    fifo_ext.to_excel(outdir / "step5_fifo_with_carry.xlsx")
    top_profit, top_loss = top10_profit_loss(fifo_ext.reset_index())
    top_profit.to_csv(outdir / "step6_top10_profit.csv", encoding="utf-8-sig", index=False)
    top_loss.to_csv(outdir / "step6_top10_loss.csv", encoding="utf-8-sig", index=False)
    top_netbuy, top_netsell = top10_netflow(fifo_ext.reset_index())
    netbuy_csv  = outdir / "step7_top10_netbuy_pnl.csv"
    netsell_csv = outdir / "step7_top10_netsell_pnl.csv"
    xlsx_path   = outdir / "step7_netbuy_netsell_pnl.xlsx"
    top_netbuy.to_csv(netbuy_csv,  encoding="utf-8-sig", index=False)
    top_netsell.to_csv(netsell_csv, encoding="utf-8-sig", index=False)
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        top_netbuy.to_excel(writer,  sheet_name="買超_TOP10", index=False)
        top_netsell.to_excel(writer, sheet_name="賣超_TOP10", index=False)

def parse_args():
    p = argparse.ArgumentParser(description="券商分點資料處理與 FIFO 撮合全流程")
    # 改成必填的位置參數，不要 default
    p.add_argument("input", type=str, help="輸入的 CSV 檔案路徑")
    p.add_argument("--outdir", type=str, default="output", help="輸出資料夾")
    p.add_argument("--fee_discount", type=float, default=0.28, help="手續費折扣 (預設 0.28)")
    p.add_argument("--day_trade_tax", type=float, default=0.0015, help="當沖交易稅率 (預設 0.0015)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # 根據輸入檔案名稱創建專屬的輸出資料夾
    input_name = Path(args.input).stem  # 取得檔名（不含副檔名）
    output_dir = Path(args.outdir) / f"analysis_{input_name}"
    
    print(f"輸入檔案: {args.input}")
    print(f"輸出資料夾: {output_dir}")
    print("=" * 50)
    
    run_pipeline(Path(args.input), output_dir, fee_discount=args.fee_discount, day_trade_tax=args.day_trade_tax)
