#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版股票券商進出明細下載工具
一鍵下載指定股票的券商買賣明細 CSV 檔案
"""

from _workspace_bootstrap import ensure_src_on_path

ensure_src_on_path()

from taiwan_stock_broker_analysis.cli.simple_downloader_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
