@echo off
chcp 65001 >nul
echo ====================================
echo   券商進出明細分析工具
echo ====================================
echo.
echo 正在分析: 2317_處理後資料_20250907_121846.csv
echo.

python broker_pipeline.py --input "2317_處理後資料_20250907_121846.csv"

echo.
echo 分析完成！結果已儲存在 output 資料夾中
echo 按任意鍵關閉視窗...
pause >nul
