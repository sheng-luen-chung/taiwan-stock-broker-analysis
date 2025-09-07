@echo off
chcp 65001 >nul
echo ====================================
echo   鴻海(2317) 券商分析處理工具
echo ====================================
echo.
echo 📊 正在處理: 2317_處理後資料_20250907_110152.csv
echo 📁 輸出目錄: output_2317
echo.

python broker_pipeline.py --input 2317_處理後資料_20250907_110152.csv --outdir output_2317

echo.
echo 🎉 處理完成！
echo.
echo 輸出檔案位置: output_2317 資料夾
echo.
echo 主要報告:
echo   📈 step5_fifo_with_carry.xlsx - FIFO 撮合詳細結果
echo   📊 step7_netbuy_netsell_pnl.xlsx - 買超賣超統計
echo   💰 step4_avg_method_pnl.xlsx - 平均價法損益
echo.

set /p open_folder="要開啟輸出資料夾嗎？ (y/n): "
if /i "%open_folder%"=="y" (
    explorer output_2317
)

echo.
echo 按任意鍵關閉視窗...
pause >nul
