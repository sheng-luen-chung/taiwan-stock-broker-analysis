# -*- coding: utf-8 -*-
"""
一鍵：爬券商進出明細 → 產生處理後 CSV → 跑分析輸出
用法：
  python run_pipeline.py 4958
  python run_pipeline.py 2330 --retries 6 --outdir output --fee-discount 0.28 --day-trade-tax 0.0015
"""

from _workspace_bootstrap import ensure_src_on_path

ensure_src_on_path()

from taiwan_stock_broker_analysis.cli.run_pipeline_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
