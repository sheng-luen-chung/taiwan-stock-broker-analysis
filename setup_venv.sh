#!/bin/bash
# 建立虛擬環境並安裝 requirements.txt
set -e
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools wheel
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  echo "⚠️ 找不到 requirements.txt，請自行安裝所需套件。"
fi
echo "✅ 完成！目前使用的 Python 解譯器："
python -c "import sys; print(sys.executable)"