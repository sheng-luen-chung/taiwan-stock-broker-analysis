# 📈 台灣證券交易所券商進出明細爬蟲工具 - 安裝指南

> 🚀 自動下載股票券商買賣明細，支援 OCR 驗證碼識別，UTF-8 編碼完美支援 Excel

## 📋 系統需求

### 基本需求
- **Python 3.7+** (建議 Python 3.8 - 3.11)
- **Windows 10/11** (其他系統未測試)
- **穩定的網路連線**

### 硬體需求
- **記憶體**: 最少 4GB RAM (建議 8GB 以上)
- **儲存空間**: 最少 1GB 可用空間
- **網路**: 穩定的網路連線 (用於下載套件和爬取資料)

## ⚠️ 重要安裝注意事項

### 🔴 ddddocr 相依性問題
**最常見的安裝問題**是 `ddddocr` 與其相依套件的版本衝突，特別是：
- `numpy` 版本衝突 (2.x vs 1.x)
- `onnxruntime` 版本不相容
- `opencv-python` 版本問題

### 💡 推薦安裝環境

我們**強烈建議**使用以下環境之一：

#### 選項一：Anaconda/Miniconda (推薦)
```bash
# 安裝 Miniconda
# 下載: https://docs.conda.io/en/latest/miniconda.html

# 建立專用環境
conda create -n stock_scraper python=3.10
conda activate stock_scraper

# 安裝套件
conda install -c conda-forge requests beautifulsoup4 lxml
pip install ddddocr
```

#### 選項二：Python 虛擬環境
```bash
# 建立虛擬環境
python -m venv stock_env

# 啟動環境 (Windows)
stock_env\Scripts\activate

# 啟動環境 (macOS/Linux)
source stock_env/bin/activate

# 升級 pip
python -m pip install --upgrade pip

# 安裝套件 (按順序)
pip install numpy==1.24.4
pip install onnxruntime==1.16.3
pip install opencv-python-headless==4.8.1.78
pip install pillow==10.0.1
pip install ddddocr==1.4.11
pip install requests beautifulsoup4 lxml
```

## 📦 Requirements.txt

建議使用以下版本組合 (已測試相容性)：

```txt
# 核心相依套件 (指定版本避免衝突)
numpy==1.24.4
onnxruntime==1.16.3
opencv-python-headless==4.8.1.78
pillow==10.0.1

# OCR 套件
ddddocr==1.4.11

# 網路爬蟲套件
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
```

## 🚀 快速安裝

### 方法一：一鍵安裝 (推薦新手)

建立 `install.bat` 檔案：
```batch
@echo off
echo 正在安裝股票爬蟲工具...
echo.

echo 第一步：安裝基礎相依套件
pip install numpy==1.24.4
pip install onnxruntime==1.16.3
pip install opencv-python-headless==4.8.1.78
pip install pillow==10.0.1

echo 第二步：安裝 OCR 套件
pip install ddddocr==1.4.11

echo 第三步：安裝網路爬蟲套件
pip install requests beautifulsoup4 lxml

echo.
echo 安裝完成！正在測試...
python -c "import ddddocr; print('✅ ddddocr 安裝成功')"
python -c "import requests; print('✅ requests 安裝成功')"
python -c "import bs4; print('✅ beautifulsoup4 安裝成功')"

echo.
echo 🎉 所有套件安裝完成！
pause
```

### 方法二：使用 requirements.txt
```bash
# 下載 requirements.txt 後執行
pip install -r requirements.txt
```

## 🔧 常見安裝問題與解決方案

### 問題 1: ddddocr 安裝失敗
```
ERROR: Failed building wheel for ddddocr
```

**解決方案**:
```bash
# 方案 A: 分步安裝
pip uninstall numpy onnxruntime ddddocr -y
pip install numpy==1.24.4
pip install onnxruntime==1.16.3
pip install ddddocr==1.4.11

# 方案 B: 使用預編譯版本
pip install ddddocr --only-binary=all

# 方案 C: 降級 Python 版本
# 如果使用 Python 3.12+，建議降至 Python 3.10
```

### 問題 2: onnxruntime 版本衝突
```
ERROR: onnxruntime requires numpy<2.0.0,>=1.21.6
```

**解決方案**:
```bash
# 強制安裝相容版本
pip uninstall numpy onnxruntime -y
pip install numpy==1.24.4
pip install onnxruntime==1.16.3
```

### 問題 3: 記憶體不足
```
MemoryError during installation
```

**解決方案**:
```bash
# 使用較少記憶體的安裝方式
pip install --no-cache-dir ddddocr
pip install --no-deps ddddocr  # 不自動安裝相依套件
```

### 問題 4: 網路連線問題
```
Could not fetch URL...
```

**解決方案**:
```bash
# 使用國內鏡像
pip install -i https://pypi.douban.com/simple/ ddddocr
# 或
pip install -i https://mirrors.aliyun.com/pypi/simple/ ddddocr
```

## ✅ 安裝驗證

執行以下測試確認安裝成功：

```python
# test_installation.py
try:
    import ddddocr
    print("✅ ddddocr: OK")
    
    import requests
    print("✅ requests: OK")
    
    import bs4
    print("✅ beautifulsoup4: OK")
    
    import lxml
    print("✅ lxml: OK")
    
    # 測試 OCR 初始化
    ocr = ddddocr.DdddOcr()
    print("✅ OCR 初始化: OK")
    
    print("\n🎉 所有套件安裝成功，可以開始使用！")
    
except ImportError as e:
    print(f"❌ 安裝失敗: {e}")
    print("請檢查安裝步驟")
```

## 🌟 推薦開發環境

### IDE 推薦
- **VS Code** + Python 擴充功能
- **PyCharm Community** (免費版)
- **Spyder** (科學計算導向)

### 除錯技巧
```python
# 檢查套件版本
import ddddocr, numpy, onnxruntime
print(f"ddddocr: {ddddocr.__version__}")
print(f"numpy: {numpy.__version__}")
print(f"onnxruntime: {onnxruntime.__version__}")
```

## 🚨 故障排除流程

如果遇到安裝問題，請按以下順序排除：

### 第一步：檢查 Python 版本
```bash
python --version
# 建議使用 Python 3.8-3.11
```

### 第二步：清理環境
```bash
pip uninstall ddddocr onnxruntime numpy opencv-python pillow -y
```

### 第三步：重新安裝
```bash
pip install numpy==1.24.4
pip install onnxruntime==1.16.3
pip install opencv-python-headless==4.8.1.78
pip install pillow==10.0.1
pip install ddddocr==1.4.11
```

### 第四步：驗證安裝
```bash
python -c "import ddddocr; print('成功')"
```

## 📞 技術支援

### 如果仍然無法安裝，請提供：
1. **作業系統版本** (Windows 10/11)
2. **Python 版本** (`python --version`)
3. **錯誤訊息完整內容**
4. **pip 版本** (`pip --version`)
5. **記憶體大小**

### 替代方案
如果 ddddocr 始終無法安裝，我們提供：
- **手動驗證碼版本** (`stock_scraper_manual.py`)
- **Docker 容器版本** (隔離環境，避免相依性問題)

## 🎯 成功安裝後

安裝成功後，您可以：

```bash
# 測試下載
python stock_scraper.py 4958

# 或使用批次檔
快速下載.bat
```

## 📚 相關文件

- **README.md** - 基本使用說明
- **快速使用指南.md** - 新手入門
- **HackMD_文檔.md** - 完整技術文檔

---

> 💡 **小提示**: 如果您是程式新手，強烈建議使用 Anaconda 環境，可以避免大部分相依性問題！

*最後更新: 2025年9月7日*
