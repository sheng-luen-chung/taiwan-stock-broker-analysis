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

Write-Host ">> 建立 Python $PyVersion 的虛擬環境..." -ForegroundColor Cyan

# 建立 .venv
py -$PyVersion -m venv .venv
if (-not $?) {
  throw "找不到 Python $PyVersion，請先安裝它（或用 'setup_venv.ps1 -PyVersion 3.12' 指定版本）"
}

# 啟用虛擬環境
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
.\.venv\Scripts\Activate.ps1

Write-Host ">> 升級 pip / setuptools / wheel..." -ForegroundColor Cyan
python -m pip install -U pip setuptools wheel

Write-Host ">> 安裝 requirements.txt 套件..." -ForegroundColor Cyan
if (Test-Path requirements.txt) {
  pip install -r requirements.txt
} else {
  Write-Host "⚠️ 專案中沒有 requirements.txt，請自行安裝所需套件。" -ForegroundColor Yellow
}

Write-Host ">> 完成！目前使用的 Python 解譯器：" -ForegroundColor Green
python -c "import sys; print(sys.executable)"
