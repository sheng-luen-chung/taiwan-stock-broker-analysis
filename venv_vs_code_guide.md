# VS Code + venv 使用說明

## 1. 為什麼要用 venv？
- 在 VS Code 執行 Python 專案時，為了避免不同電腦的套件版本不一致，會使用 venv 建立專屬的虛擬環境。

## 2. 如何建立 venv？
- 在終端機輸入：
  
  ```sh
  python -m venv .venv
  ```
  
- 這會產生 .venv 目錄，裡面 Scripts 資料夾下有 Activate.ps1。

## 3. 啟用 venv
- 在 PowerShell 輸入：
  
  ```sh
  .\.venv\Scripts\Activate.ps1
  ```
  
- PowerShell 前面會出現 `(.venv)` 前綴，表示已進入虛擬環境。

## 4. 安裝套件
- 第一次建置時，記得執行：
  
  ```sh
  pip install -r requirements.txt
  ```
  
- 安裝專案所需套件（注意檔名是 requirements.txt）。

## 5. 設定 VS Code 解譯器
- 在 VS Code 執行「Python: Select Interpreter」，選擇 .venv 內的 python.exe。

## 6. 檢查 Python 路徑
- 可以用：
  
  ```sh
  where python
  ```
  
- 檢查目前使用的 Python 路徑，確認是否指向 .venv。

## 7. 自動啟用 venv
- 之後每次開啟專案，若 .vscode/settings.json 有：
  
  ```json
  "python.terminal.activateEnvironment": true
  ```
  
- VS Code 會自動執行 Activate.ps1，進入虛擬環境，直接在此環境下執行 python 程式即可。

---
如需更正或補充，請隨時更新本文件！
