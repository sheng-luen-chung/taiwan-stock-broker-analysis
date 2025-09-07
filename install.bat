@echo off
chcp 65001 >nul
echo ========================================
echo   股票爬蟲工具 - 自動安裝程式
echo ========================================
echo.
echo 此程式將自動安裝所需的 Python 套件
echo 建議在虛擬環境中執行以避免衝突
echo.

set /p confirm="確定要開始安裝嗎？ (y/n): "
if /i not "%confirm%"=="y" (
    echo 安裝已取消
    pause
    exit /b
)

echo.
echo 📦 開始安裝套件...
echo.

echo ⏳ 第一步：升級 pip
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ pip 升級失敗
    pause
    exit /b 1
)

echo.
echo ⏳ 第二步：安裝核心相依套件 (按順序安裝避免衝突)
echo.

echo 安裝 numpy...
pip install numpy==1.24.4
if errorlevel 1 (
    echo ❌ numpy 安裝失敗
    pause
    exit /b 1
)

echo 安裝 onnxruntime...
pip install onnxruntime==1.16.3
if errorlevel 1 (
    echo ❌ onnxruntime 安裝失敗
    pause
    exit /b 1
)

echo 安裝 opencv-python-headless...
pip install opencv-python-headless==4.8.1.78
if errorlevel 1 (
    echo ❌ opencv-python-headless 安裝失敗
    pause
    exit /b 1
)

echo 安裝 pillow...
pip install pillow==10.0.1
if errorlevel 1 (
    echo ❌ pillow 安裝失敗
    pause
    exit /b 1
)

echo.
echo ⏳ 第三步：安裝 OCR 套件
echo.

echo 安裝 ddddocr...
pip install ddddocr==1.4.11
if errorlevel 1 (
    echo ❌ ddddocr 安裝失敗
    echo 💡 如果持續失敗，請查看 INSTALL.md 中的故障排除
    pause
    exit /b 1
)

echo.
echo ⏳ 第四步：安裝網路爬蟲套件
echo.

echo 安裝 requests...
pip install requests
if errorlevel 1 (
    echo ❌ requests 安裝失敗
    pause
    exit /b 1
)

echo 安裝 beautifulsoup4...
pip install beautifulsoup4
if errorlevel 1 (
    echo ❌ beautifulsoup4 安裝失敗
    pause
    exit /b 1
)

echo 安裝 lxml...
pip install lxml
if errorlevel 1 (
    echo ❌ lxml 安裝失敗
    pause
    exit /b 1
)

echo.
echo ✅ 所有套件安裝完成！
echo.
echo 🔍 正在驗證安裝...
echo.

python -c "import ddddocr; print('✅ ddddocr 安裝成功')" 2>nul
if errorlevel 1 (
    echo ❌ ddddocr 驗證失敗
    goto error
)

python -c "import requests; print('✅ requests 安裝成功')" 2>nul
if errorlevel 1 (
    echo ❌ requests 驗證失敗
    goto error
)

python -c "import bs4; print('✅ beautifulsoup4 安裝成功')" 2>nul
if errorlevel 1 (
    echo ❌ beautifulsoup4 驗證失敗
    goto error
)

python -c "import lxml; print('✅ lxml 安裝成功')" 2>nul
if errorlevel 1 (
    echo ❌ lxml 驗證失敗
    goto error
)

echo.
echo 🎉 安裝驗證成功！
echo.
echo 現在您可以使用以下方式開始：
echo   1. 雙擊 "快速下載.bat"
echo   2. 執行 "python stock_scraper.py 股票代碼"
echo.
echo 範例: python stock_scraper.py 4958
echo.
pause
exit /b 0

:error
echo.
echo ❌ 安裝過程中發生錯誤
echo.
echo 請檢查：
echo   1. Python 版本是否為 3.7+ (建議 3.8-3.11)
echo   2. 網路連線是否正常
echo   3. 是否有足夠的磁碟空間
echo.
echo 詳細故障排除請參考 INSTALL.md
echo.
pause
exit /b 1
