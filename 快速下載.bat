@echo off
chcp 65001 >nul
echo ====================================
echo   台灣證券交易所券商進出明細爬蟲工具
echo ====================================
echo.
echo 📊 CSV 檔案將以 UTF-8 編碼儲存，可直接用 Excel 開啟
echo.
echo 常見股票代碼:
echo   2317 - 鴻海
echo   2330 - 台積電
echo   4958 - 臻鼎-KY
echo   2454 - 聯發科
echo   2412 - 中華電
echo   1301 - 台塑
echo.

set /p stock_code="請輸入股票代碼: "

if "%stock_code%"=="" (
    echo 錯誤: 股票代碼不能為空
    pause
    goto :eof
)

echo.
echo 開始下載股票代碼 %stock_code% 的券商進出明細...
echo.

python stock_scraper.py %stock_code%

echo.
echo 按任意鍵關閉視窗...
pause >nul
