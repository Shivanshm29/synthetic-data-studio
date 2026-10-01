import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.datascout.datascout_engine import DataScoutEngine
from app.datascout.datascout_schema import DataScoutResponse
from app.datascout.integrations.hf_search import search_huggingface_datasets
from app.datascout.integrations.kaggle_search import search_kaggle_datasets
from app.datascout.profiler import DatasetProfiler


class TestDataScoutEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DataScoutEngine()

    def test_heuristic_fallback_known_dataset(self):
        res = self.engine.analyze("I need titanic passenger survival records")
        self.assertIsInstance(res, DataScoutResponse)
        self.assertEqual(res.strategy, "Existing Dataset")
        self.assertTrue(len(res.existing_datasets) > 0)
        self.assertIn("Titanic", res.existing_datasets[0].name)

    def test_heuristic_fallback_synthetic(self):
        res = self.engine.analyze("Generate xyz_nonexistent_dataset_quantum_alien_flux_99999")
        self.assertIsInstance(res, DataScoutResponse)
        self.assertEqual(res.strategy, "Fully Synthetic Generation")
        self.assertGreaterEqual(res.confidence, 0.8)

    def test_hf_search(self):
        res = search_huggingface_datasets("finance", limit=2)
        self.assertIsInstance(res, list)

    def test_kaggle_search(self):
        res = search_kaggle_datasets("housing", limit=2)
        self.assertIsInstance(res, list)

    def test_profiler(self):
        csv_data = b"id,name,age\n1,Alice,30\n2,Bob,25\n3,Charlie,35"
        report = DatasetProfiler.profile_file("sample.csv", csv_data)
        self.assertEqual(report.total_rows, 3)
        self.assertEqual(report.total_columns, 3)
        self.assertIn("id", report.primary_keys)


if __name__ == "__main__":
    unittest.main()

