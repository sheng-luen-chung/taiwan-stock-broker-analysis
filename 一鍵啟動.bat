@echo off
REM 啟動虛擬環境、安裝套件並執行 pipeline

REM 啟動 venv
call H:\venvs\taiwan-stock-broker-analysis-py312\Scripts\activate.bat

REM 顯示 Python 版本
python --version

REM 安裝 requirements.txt 內套件
pip install -r requirements.txt

REM 執行 pipeline（可自行修改參數）
python run_pipeline.py 4958

pause
