<#
.SYNOPSIS
  建立專案專用的 Python 虛擬環境，並安裝 requirements.txt 內的套件。

.DESCRIPTION
  - 預設使用 Python 3.11
  - 建立 .venv
  - 升級 pip / setuptools / wheel
  - 安裝 requirements.txt
  - 最後顯示使用的解譯器路徑
#>

param(
  [string]$PyVersion = "3.11"
)

Write-Host ">> Creating Python $PyVersion virtual environment..." -ForegroundColor Cyan

# 建立 .venv
py -$PyVersion -m venv .venv
if (-not $?) {
  throw "Python $PyVersion not found. Please install it first (or use 'setup_venv.ps1 -PyVersion 3.12' to specify version)."
}

# 啟用虛擬環境
.\.venv\Scripts\Activate.ps1

Write-Host ">> Upgrading pip / setuptools / wheel..." -ForegroundColor Cyan
python -m pip install -U pip setuptools wheel

Write-Host ">> Installing requirements.txt packages..." -ForegroundColor Cyan
if (Test-Path requirements.txt) {
  pip install -r requirements.txt
} else {
  Write-Host "[Warning] requirements.txt not found. Please install required packages manually." -ForegroundColor Yellow
}

Write-Host ">> Done! Current Python interpreter:" -ForegroundColor Green
python -c "import sys; print(sys.executable)"
