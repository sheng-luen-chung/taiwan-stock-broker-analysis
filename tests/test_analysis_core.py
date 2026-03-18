import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"

for path_text in [str(REPO_ROOT), str(SRC_PATH)]:
    if path_text not in sys.path:
        sys.path.insert(0, path_text)

from taiwan_stock_broker_analysis.analysis.core import analyze_csv_file, normalize_to_mother, read_flat_csv


SAMPLE_PROCESSED_CSV = """股票代碼: 0000 - 券商買賣明細
下載時間: 2026-03-18 12:00:00

序號,券商,價格,買進股數,賣出股數,,序號,券商,價格,買進股數,賣出股數
1,1234元大台北,100,1000,0,,2,9876凱基台北,101,0,1000
3,富邦建國,102,2000,0,,4,富邦建國,103,0,1000
"""


class AnalysisCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="analysis_core_test_"))
        self.input_csv = self.temp_dir / "sample_processed.csv"
        self.input_csv.write_text(SAMPLE_PROCESSED_CSV, encoding="utf-8-sig")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_normalize_to_mother_removes_digits_and_branch_suffix(self):
        self.assertEqual(normalize_to_mother("1234元大台北"), "元大")
        self.assertEqual(normalize_to_mother("9876凱基台北"), "凱基")
        self.assertEqual(normalize_to_mother("富邦建國"), "富邦")
        self.assertEqual(normalize_to_mother("9A8F永豐敦南"), "永豐")
        self.assertEqual(normalize_to_mother("c國票敦北"), "國票")
        self.assertEqual(normalize_to_mother("u元大府城"), "元大")

    def test_read_flat_csv_flattens_both_csv_groups(self):
        flat = read_flat_csv(self.input_csv)

        self.assertEqual(len(flat), 4)
        self.assertListEqual(flat["序號"].astype(int).tolist(), [1, 2, 3, 4])
        self.assertIn("1234元大台北", flat["券商"].tolist())
        self.assertIn("9876凱基台北", flat["券商"].tolist())

    def test_analyze_csv_file_generates_expected_reports(self):
        outdir = self.temp_dir / "output"

        analyze_csv_file(self.input_csv, outdir, fee_discount=0.28, day_trade_tax=0.0015)

        expected_files = [
            "step1_flattened.csv",
            "step2_branch_summary.csv",
            "step2_branch_summary.xlsx",
            "step3_mother_summary.csv",
            "step3_mother_summary.xlsx",
            "step4_avg_method_pnl.csv",
            "step4_avg_method_pnl.xlsx",
            "step5_fifo_with_carry.csv",
            "step5_fifo_with_carry.xlsx",
            "step6_top10_profit.csv",
            "step6_top10_loss.csv",
            "step7_top10_netbuy_pnl.csv",
            "step7_top10_netsell_pnl.csv",
            "step7_netbuy_netsell_pnl.xlsx",
        ]

        for filename in expected_files:
            self.assertTrue((outdir / filename).exists(), f"missing report: {filename}")


if __name__ == "__main__":
    unittest.main()