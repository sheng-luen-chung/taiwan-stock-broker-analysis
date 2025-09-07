# 台灣證券交易所券商進出明細爬蟲工具

這個工具可以自動下載指定股票代碼的券商買賣明細 CSV 檔案。

## 功能特色

- 🚀 **一鍵下載**: 輸入股票代碼即可自動下載 CSV 檔案
- 🔍 **自動識別**: 使用 OCR 技術自動識別驗證碼
- 📊 **即時分析**: 下載完成後立即顯示買賣超統計
- 🔄 **自動重試**: 驗證碼錯誤時自動重試
- 💾 **自動命名**: CSV 檔案自動以股票代碼和時間命名
- 📈 **深度分析**: 支援券商進出 FIFO 撮合分析
- 🗂️ **分類儲存**: 不同檔案的分析結果自動分開儲存
- 🎯 **多種版本**: 提供 OCR 自動版和手動驗證碼版

## 安裝需求

### 快速安裝 (推薦)
1. **自動安裝**: 雙擊 `install.bat` 自動安裝所有套件
2. **驗證安裝**: 執行 `python check_installation.py` 檢查安裝結果
   - 自動檢查 Python 版本
   - 驗證所有必要套件是否正確安裝
   - 測試 OCR 引擎初始化
   - 檢查網路連線狀態
   - 提供詳細的診斷報告

### 手動安裝
首先安裝必要的套件：

```bash
# 推薦按此順序安裝避免版本衝突
pip install numpy==1.24.4
pip install onnxruntime==1.16.3
pip install opencv-python-headless==4.8.1.78
pip install pillow==10.0.1
pip install ddddocr==1.4.11
pip install requests beautifulsoup4 lxml
```

### 詳細安裝指南
如果遇到安裝問題，請參考 **[INSTALL.md](INSTALL.md)** 完整安裝指南

## 使用方法

### 一、股票資料下載

#### 方法一：Windows 批次檔（最簡單）

```bash
# 雙擊執行批次檔
快速下載.bat
```
然後輸入股票代碼即可自動下載

#### 方法二：命令列參數

```bash
# 下載鴻海(2317)的券商進出明細
python stock_scraper.py 2317

# 下載臻鼎-KY(4958)的券商進出明細  
python stock_scraper.py 4958

# 如果 OCR 安裝有問題，使用手動版本
python stock_scraper_manual.py 2317
```

#### 方法三：互動式輸入

```bash
# 直接執行，然後輸入股票代碼
python stock_scraper.py

# 或使用簡化版
python simple_downloader.py
```

#### 方法四：設定重試次數

```bash
# 設定最大重試 10 次
python stock_scraper.py 2317 --retries 10
```

### 二、券商資料分析

下載完 CSV 檔案後，可以使用券商分析工具：

#### 方法一：使用命令列指定檔案

```bash
# 分析指定的 CSV 檔案
python broker_pipeline.py --input "股票代碼_處理後資料_時間.csv"

# 範例
python broker_pipeline.py --input "2317_處理後資料_20250907_110152.csv"
```

#### 方法二：使用專用批次檔

```bash
# 雙擊執行特定分析
分析2317_121846.bat
處理鴻海2317.bat
```

### 券商分析功能包含：
- 📊 **Step 1**: 資料展平處理
- 🏢 **Step 2**: 分點券商統計
- 🏛️ **Step 3**: 母券商統計  
- 💰 **Step 4**: 平均價格法損益分析
- 📈 **Step 5**: FIFO 法損益分析（含結轉）
- 🏆 **Step 6**: 前十大獲利/虧損券商
- 🔄 **Step 7**: 淨買賣超分析

## 輸出結果

### 股票資料下載結果

程式執行後會：

1. **下載 CSV 檔案**: 檔案命名格式為 `{股票代碼}_爬蟲資料_{時間戳記}.csv`
2. **處理後資料**: 自動生成 `{股票代碼}_處理後資料_{時間戳記}.csv`
3. **顯示統計分析**: 包括總交易筆數、券商家數、前10大買超/賣超券商

### 券商分析結果

使用 `broker_pipeline.py` 分析後會在 `output/analysis_[檔案名]/` 資料夾中生成：

#### CSV 檔案：
- `step1_flattened.csv` - 展平的原始資料
- `step2_branch_summary.csv` - 分點券商統計
- `step3_mother_summary.csv` - 母券商統計
- `step4_avg_method_pnl.csv` - 平均價格法損益
- `step5_fifo_with_carry.csv` - FIFO法損益（含結轉）
- `step6_top10_profit.csv` - 前十大獲利券商
- `step6_top10_loss.csv` - 前十大虧損券商
- `step7_top10_netbuy_pnl.csv` - 前十大淨買超券商
- `step7_top10_netsell_pnl.csv` - 前十大淨賣超券商

#### Excel 檔案：
- `step2_branch_summary.xlsx` - 分點券商統計（Excel版）
- `step3_mother_summary.xlsx` - 母券商統計（Excel版）
- `step4_avg_method_pnl.xlsx` - 平均價格法損益（Excel版）
- `step5_fifo_with_carry.xlsx` - FIFO法損益（Excel版）
- `step7_netbuy_netsell_pnl.xlsx` - 淨買賣超分析（Excel版）

### 範例輸出

```
[2025-09-07 10:30:15] 開始爬取股票代碼: 4958
[2025-09-07 10:30:16] 第 1 次嘗試...
[2025-09-07 10:30:16] 正在連接證交所網站...
[2025-09-07 10:30:17] 正在下載驗證碼圖片...
[2025-09-07 10:30:18] OCR 識別結果: c4p9j
[2025-09-07 10:30:18] 正在提交查詢表單...
[2025-09-07 10:30:19] 正在下載 CSV 檔案...
[2025-09-07 10:30:20] 成功下載！檔案已儲存為: 4958_爬蟲資料_20250907_103020.csv
[2025-09-07 10:30:20] === 資料分析結果 (股票代碼: 4958) ===
[2025-09-07 10:30:20] 總交易筆數: 5882
[2025-09-07 10:30:20] 券商家數: 203

🎉 成功完成！
📄 CSV 檔案: 4958_爬蟲資料_20250907_103020.csv
📂 儲存位置: G:\我的雲端硬碟\broker_analysis\4958_爬蟲資料_20250907_103020.csv
```

## 常見股票代碼

| 代碼 | 公司名稱 | 產業類別 | 代碼 | 公司名稱 | 產業類別 |
|------|----------|----------|------|----------|----------|
| **2330** | 台積電 | 半導體 | **2317** | 鴻海 | 電子零組件 |
| **2454** | 聯發科 | 半導體 | **2412** | 中華電 | 電信服務 |
| **4958** | 臻鼎-KY | 印刷電路板 | **1301** | 台塑 | 塑膠工業 |
| **2881** | 富邦金 | 金融保險 | **2882** | 國泰金 | 金融保險 |
| **1216** | 統一 | 食品工業 | **1101** | 台泥 | 水泥工業 |

## CSV 檔案格式

下載的 CSV 檔案包含以下欄位：
- 序號
- 券商名稱
- 價格
- 買進股數
- 賣出股數

## 故障排除

### 安裝問題診斷
首先執行診斷工具檢查系統狀態：
```bash
python check_installation.py
```
這個工具會自動檢查：
- Python 版本是否符合需求
- 所有必要套件是否正確安裝
- OCR 引擎是否能正常初始化
- 網路連線是否正常

### 驗證碼識別失敗
- 程式會自動重試，預設最多重試 5 次
- 可使用 `--retries` 參數增加重試次數

### 網路連線問題
- 確認網路連線正常
- 確認可以正常訪問 https://bsr.twse.com.tw/

### 套件安裝問題
```bash
# 如果 ddddocr 安裝失敗，嘗試：
pip install ddddocr onnxruntime --no-deps
pip install opencv-python pillow numpy

# 或執行完整診斷
python check_installation.py
```

## 注意事項

- 此工具僅用於學術研究和個人使用
- 請遵守證交所網站的使用條款
- 避免過於頻繁的請求，以免對伺服器造成負擔
- OCR 識別可能偶爾失敗，程式會自動重試
- **建議使用時間**: 收盤後（下午 2:30 以後）數據較完整
- **間隔控制**: 建議每次下載間隔至少 10 秒

## 專案檔案

### 主要程式
- `stock_scraper.py` - 主程式（完整功能版，支援 OCR 自動識別驗證碼）
- `stock_scraper_manual.py` - 手動驗證碼版本（適用於 OCR 安裝困難的情況）
- `simple_downloader.py` - 簡化版下載器
- `broker_pipeline.py` - 券商數據分析管道（FIFO 撮合分析）
- `快速下載.bat` - Windows 批次檔，雙擊即可使用

### 券商分析工具
- `broker_pipeline.py` - 完整的券商進出分析流程
- `分析2317_121846.bat` - 特定檔案分析批次檔範例
- `處理鴻海2317.bat` - 鴻海股票專用分析批次檔

### 安裝相關
- `install.bat` - 自動安裝腳本
- `check_installation.py` - 安裝驗證程式（檢查套件安裝狀況）
- `requirements.txt` - 套件相依性清單
- `INSTALL.md` - 詳細安裝指南

### 說明文件
- `README.md` - 詳細使用說明（本檔案）
- `快速使用指南.md` - 快速入門指南
- `HackMD_文檔.md` - 完整技術文檔

### 測試工具
- `csv_encoding_test.py` - CSV 編碼測試工具

### 輸出資料夾
- `output/` - 分析結果輸出資料夾
  - `analysis_[檔案名]/` - 各 CSV 檔案的專屬分析結果
  - 包含：展平資料、分點統計、母券商統計、FIFO 損益分析等

## 技術說明

- 使用 `requests` 處理 HTTP 請求
- 使用 `BeautifulSoup` 解析 HTML
- 使用 `ddddocr` 進行驗證碼識別
- 自動處理 Session 和 Cookie 管理
