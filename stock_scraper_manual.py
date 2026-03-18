#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣證券交易所券商進出明細爬蟲工具 (手動驗證碼版本)
自動下載指定股票代碼的券商買賣明細 CSV 檔案

使用方法:
    python stock_scraper_manual.py 2317
    python stock_scraper_manual.py 4958
"""

from _workspace_bootstrap import ensure_src_on_path

ensure_src_on_path()

from taiwan_stock_broker_analysis.cli.stock_scraper_manual_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
