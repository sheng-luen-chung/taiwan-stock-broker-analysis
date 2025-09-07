# 📈 台灣證券交易所券商進出明細自動爬蟲工具

> 🚀 一鍵下載股票券商買賣明細，自動識別驗證碼，無需手動操作！

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Working-brightgreen.svg)](https://github.com)

---

## 🎯 專案概述

這是一個自動化的股票券商進出明細爬蟲工具，能夠從台灣證券交易所網站自動下載指定股票代碼的券商買賣明細 CSV 檔案。

### ✨ 核心功能

- 🔍 **自動驗證碼識別** - 使用 ddddocr OCR 技術自動識別驗證碼
- 📊 **一鍵數據下載** - 輸入股票代碼即可自動下載完整 CSV 資料
- 🔄 **智能重試機制** - 驗證碼錯誤時自動重試，最大化成功率
- 📈 **即時數據分析** - 自動計算券商買賣超排行榜
- 💾 **自動檔案管理** - CSV 檔案自動命名包含時間戳記
- 🎨 **多種使用方式** - 支援批次檔、命令列、互動式操作
- 📊 **深度券商分析** - FIFO 撮合損益分析、母券商統計
- 🗂️ **智能分類儲存** - 不同檔案分析結果自動分開儲存
- 📋 **多格式輸出** - 同時支援 CSV 和 Excel 格式輸出

---

## 🛠️ 技術架構

### 核心技術棧
- **Python 3.7+** - 主要開發語言
- **requests** - HTTP 請求處理
- **BeautifulSoup4** - HTML 解析
- **ddddocr** - 驗證碼自動識別
- **lxml** - XML/HTML 解析器

### 程式架構
```
broker_analysis/
├── 主要程式
│   ├── stock_scraper.py              # 主程式（OCR 自動版）
│   ├── stock_scraper_manual.py       # 手動驗證碼版本
│   ├── simple_downloader.py          # 簡化版下載器
│   └── broker_pipeline.py            # 券商數據深度分析工具
├── 批次檔工具
│   ├── 快速下載.bat                  # 一鍵下載股票資料
│   ├── 分析2317_121846.bat          # 特定檔案分析範例
│   ├── 處理鴻海2317.bat              # 鴻海股票專用分析
│   └── install.bat                   # 自動安裝腳本
├── 安裝與測試
│   ├── check_installation.py         # 安裝驗證程式
│   ├── csv_encoding_test.py          # CSV 編碼測試工具
│   └── requirements.txt              # 套件相依性清單
├── 說明文件
│   ├── README.md                     # 詳細使用說明
│   ├── 快速使用指南.md               # 快速入門指南
│   ├── HackMD_文檔.md               # 完整技術文檔
│   └── INSTALL.md                    # 詳細安裝指南
└── 輸出資料夾
    ├── output/                       # 分析結果輸出
    │   └── analysis_[檔案名]/       # 各檔案專屬分析結果
    ├── *_爬蟲資料_*.csv             # 原始下載資料
    └── *_處理後資料_*.csv           # 清理處理後資料
```

---

## 🚀 快速開始

### 環境需求

```bash
# 安裝必要套件（推薦使用 install.bat 自動安裝）
pip install requests beautifulsoup4 ddddocr lxml pandas openpyxl
```

### 使用方法

#### 第一步：下載股票資料

##### 方法一：Windows 批次檔（推薦）
```bash
# 雙擊執行
快速下載.bat
```

##### 方法二：命令列參數
```bash
# OCR 自動版（推薦）
python stock_scraper.py 2317   # 鴻海
python stock_scraper.py 4958   # 臻鼎-KY
python stock_scraper.py 2330   # 台積電

# 手動驗證碼版（OCR 安裝困難時）
python stock_scraper_manual.py 2317

# 簡化版
python simple_downloader.py
```

##### 方法三：互動式輸入
```bash
# 互動式操作
python stock_scraper.py
```

##### 方法四：設定重試次數
```bash
# 自訂重試次數
python stock_scraper.py 2317 --retries 10
```

#### 第二步：深度券商分析（可選）

下載完成後，可以使用券商分析工具進行深度分析：

##### 方法一：使用批次檔
```bash
# 雙擊執行特定分析
分析2317_121846.bat
處理鴻海2317.bat
```

##### 方法二：命令列指定檔案
```bash
# 分析指定檔案
python broker_pipeline.py --input "2317_處理後資料_20250907_110152.csv"

# 輸出到指定資料夾
python broker_pipeline.py --input "檔案.csv" --outdir "custom_output"
```

#### 券商分析功能包含：
- 📊 **Step 1**: 資料展平處理
- 🏢 **Step 2**: 分點券商統計（CSV + Excel）
- 🏛️ **Step 3**: 母券商統計（CSV + Excel）
- 💰 **Step 4**: 平均價格法損益分析（CSV + Excel）
- 📈 **Step 5**: FIFO 法損益分析含結轉（CSV + Excel）
- 🏆 **Step 6**: 前十大獲利/虧損券商（CSV）
- 🔄 **Step 7**: 淨買賣超分析（CSV + Excel）

---

## 📊 輸出範例

### 控制台輸出
```
[2025-09-07 10:30:15] 開始爬取股票代碼: 4958
[2025-09-07 10:30:16] 第 1 次嘗試...
[2025-09-07 10:30:16] 正在連接證交所網站...
[2025-09-07 10:30:17] 正在下載驗證碼圖片...
[2025-09-07 10:30:18] OCR 識別結果: c4p9j
[2025-09-07 10:30:18] 正在提交查詢表單...
[2025-09-07 10:30:19] 正在下載 CSV 檔案...
[2025-09-07 10:30:20] 成功下載！檔案已儲存為: 4958_爬蟲資料_20250907_103020.csv

=== 資料分析結果 (股票代碼: 4958) ===
總交易筆數: 5882
券商家數: 203

🔥 前 10 大買超券商:
   1. 元大永豐       買超:      798張 (買:      800張, 賣:        2張)
   2. 凱基台北       買超:      695張 (買:      702張, 賣:        7張)
   3. 台灣摩根       買超:      429張 (買:      490張, 賣:       61張)
   4. 富邦台北       買超:      385張 (買:      401張, 賣:       16張)
   5. 元富台北       買超:      321張 (買:      355張, 賣:       34張)

📉 前 10 大賣超券商:
   1. 群益台北       賣超:      512張 (買:       45張, 賣:      557張)
   2. 統一台北       賣超:      389張 (買:       78張, 賣:      467張)
   3. 永豐台北       賣超:      298張 (買:      123張, 賣:      421張)

🎉 成功完成！
📄 CSV 檔案: 4958_爬蟲資料_20250907_103020.csv
📂 儲存位置: G:\我的雲端硬碟\broker_analysis\4958_爬蟲資料_20250907_103020.csv
```

### CSV 檔案格式
| 欄位名稱 | 說明 |
|----------|------|
| 序號 | 交易序號 |
| 券商名稱 | 券商公司名稱 |
| 價格 | 交易價格 |
| 買進股數 | 買進股數（單位：張） |
| 賣出股數 | 賣出股數（單位：張） |

---

## 📋 常用股票代碼

| 代碼 | 公司名稱 | 產業類別 | 代碼 | 公司名稱 | 產業類別 |
|------|----------|----------|------|----------|----------|
| **2330** | 台積電 | 半導體 | **2317** | 鴻海 | 電子零組件 |
| **2454** | 聯發科 | 半導體 | **2412** | 中華電 | 電信服務 |
| **4958** | 臻鼎-KY | 印刷電路板 | **1301** | 台塑 | 塑膠工業 |
| **2881** | 富邦金 | 金融保險 | **2882** | 國泰金 | 金融保險 |
| **1216** | 統一 | 食品工業 | **1101** | 台泥 | 水泥工業 |

---

## 🔧 進階功能

### 自動重試機制
```python
# 預設重試 5 次，可自訂
python stock_scraper.py 2317 --retries 10
```

### 批次下載多檔案
```bash
# 建立批次檔
echo python stock_scraper.py 2317 > download_multiple.bat
echo python stock_scraper.py 2330 >> download_multiple.bat
echo python stock_scraper.py 4958 >> download_multiple.bat
```

### 排程自動下載
```bash
# Windows 工作排程器
schtasks /create /tn "股票爬蟲" /tr "python stock_scraper.py 2317" /sc daily /st 15:30
```

---

## 🛠️ 故障排除

### 常見問題與解決方案

#### 1. 套件安裝問題
```bash
# 方案一：標準安裝
pip install requests beautifulsoup4 ddddocr lxml

# 方案二：如果 ddddocr 安裝失敗
pip install ddddocr onnxruntime --no-deps
pip install opencv-python pillow numpy

# 方案三：使用 conda
conda install -c conda-forge requests beautifulsoup4 lxml
pip install ddddocr
```

#### 2. 驗證碼識別率問題
- **自動重試**: 程式會自動重試 5 次
- **網路穩定性**: 確保網路連線穩定
- **增加重試次數**: 使用 `--retries` 參數

#### 3. 網路連線問題
```bash
# 檢查證交所網站連線
ping bsr.twse.com.tw

# 檢查防火牆設定
# 確保 Python.exe 有網路存取權限
```

#### 4. Python 環境問題
```bash
# 檢查 Python 版本
python --version

# 檢查已安裝套件
pip list | findstr ddddocr
```

---

## 📊 效能優化

### 建議使用時間
- **最佳時間**: 收盤後 15:00 - 18:00
- **避免時間**: 開盤時段 09:00 - 13:30（交易量大，網站負載高）

### 使用頻率控制
```python
import time

# 在下載間隔加入延遲
time.sleep(10)  # 間隔 10 秒
```

### 批次處理建議
```bash
# 建議每次間隔 10-15 秒
python stock_scraper.py 2317
timeout /t 15 /nobreak > nul
python stock_scraper.py 2330
timeout /t 15 /nobreak > nul
python stock_scraper.py 4958
```

---

## 🔒 法律聲明與使用須知

### 使用條款
- ✅ **學術研究使用** - 僅供學術研究和個人分析使用
- ✅ **遵守網站條款** - 請遵守台灣證券交易所網站使用條款
- ⚠️ **頻率控制** - 避免過於頻繁請求，以免對伺服器造成負擔
- ❌ **商業用途** - 禁止用於商業營利目的

### 免責聲明
- 本工具僅供技術學習交流使用
- 使用者需自行承擔使用風險
- 作者不對因使用本工具造成的任何損失負責
- 請確保遵守相關法律法規

---

## 🤝 貢獻指南

### 回報問題
如果您遇到問題，請提供以下資訊：
- 作業系統版本
- Python 版本
- 錯誤訊息截圖
- 使用的股票代碼

### 功能建議
歡迎提出新功能建議：
- 支援更多資料格式（Excel、JSON）
- 增加技術分析指標
- 資料視覺化功能
- 多股票批次分析

---

## 📝 更新日誌

### v1.0.0 (2025-09-07)
- ✨ 首次發布
- 🔍 實現 ddddocr 自動驗證碼識別
- 📊 完整券商買賣超分析功能
- 🚀 支援多種使用方式
- 📁 自動檔案管理和命名

### 未來規劃
- 📈 加入技術分析指標
- 📊 Excel 格式輸出
- 🎨 圖表視覺化
- 🔔 Line Bot 通知功能
- ☁️ 雲端部署版本

---

## 📞 聯絡資訊

如有任何問題或建議，歡迎聯絡：

- 📧 **Email**: [您的信箱]
- 💬 **GitHub**: [您的 GitHub]
- 📱 **Line**: [您的 Line ID]

---

## 🙏 致謝

感謝以下開源專案的貢獻：
- [ddddocr](https://github.com/sml2h3/ddddocr) - 驗證碼識別
- [requests](https://github.com/psf/requests) - HTTP 請求庫
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML 解析
- [台灣證券交易所](https://www.twse.com.tw/) - 資料來源

---

> 🎉 **現在就開始使用吧！** 雙擊 `快速下載.bat` 或執行 `python stock_scraper.py 股票代碼`

---

*最後更新時間: 2025年9月7日*
