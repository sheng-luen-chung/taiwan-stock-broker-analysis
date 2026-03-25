# 一鍵啟動與檢查 PowerShell 腳本
# 執行方式：在 PowerShell 輸入 ./一鍵啟動.ps1

# 啟動虛擬環境
$venvPath = "H:\venvs\taiwan-stock-broker-analysis-py312\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "[OK] 找到虛擬環境，啟動中..."
    . $venvPath
} else {
    Write-Host "[錯誤] 找不到虛擬環境，請先建立 venv！" -ForegroundColor Red
    exit 1
}

# 顯示 Python 版本
$pyVer = python --version
Write-Host "[Python 版本] $pyVer"
if ($pyVer -notmatch "3.12") {
    Write-Host "[警告] Python 版本不是 3.12，請確認！" -ForegroundColor Yellow
}

# 安裝 requirements.txt 內套件
Write-Host "[INFO] 安裝 requirements.txt 依賴..."
pip install -r requirements.txt

# 執行 pipeline（可自行修改參數）
Write-Host "[INFO] 執行 pipeline..."
python run_pipeline.py 4958
