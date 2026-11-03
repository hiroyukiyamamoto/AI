"""Offline regression checks for the public demos."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
MICROBIOME = ROOT / "apps/16s-microbiome-learning-app"
sys.path.insert(0, str(MICROBIOME))
from upload_validation import parse_uploads, MAX_BYTES
from data_generator import get_preset_datasets, generate_mock_16s_data

META = b"SampleID,Group\nS1,A\nS2,A\nS3,B\nS4,B\n"
COUNTS = b"SampleID,ASV1,ASV2\nS1,12,3\nS2,10,5\nS3,4,11\nS4,3,12\n"

class CsvBoundaryTests(unittest.TestCase):
    def test_valid_input_and_statistics(self):
        from modules.step4_diversity import compute_alpha_diversity, compute_bray_curtis
        meta, counts = parse_uploads(META, COUNTS)
        self.assertEqual(len(compute_alpha_diversity(counts)), 4)
        self.assertEqual(compute_bray_curtis(counts).shape, (4, 4))

    def test_rejects_unsafe_or_unbounded_input(self):
        cases = [
            (META + b"S5,C\n", COUNTS),
            (META.replace(b"S1,A", b"S1,=FORMULA"), COUNTS),
            (META.replace(b"S1,A", b"S1,<script>"), COUNTS),
            (META.replace(b"S4,B", b"S3,B"), COUNTS),
            (META.replace(b"S4,B", b"S4,A"), COUNTS),
            (META.replace(b"SampleID,Group", b"SampleID,Group,Name"), COUNTS),
            (META, COUNTS.replace(b"12,3", b"-1,3")),
            (META, COUNTS.replace(b"12,3", b"inf,3")),
            (META, COUNTS.replace(b"12,3", b"0,0")),
            (META, COUNTS.replace(b"ASV1,ASV2", b"ASV1,ASV1")),
            (b"x" * (MAX_BYTES + 1), COUNTS),
        ]
        for metadata, counts in cases:
            with self.subTest(metadata_length=len(metadata), counts_length=len(counts)):
                with self.assertRaises(ValueError):
                    parse_uploads(metadata, counts)

    def test_presets_are_generated_and_finite(self):
        import numpy as np
        from modules.step5_stats import compute_differential_abundance
        for key in get_preset_datasets():
            metadata, counts, taxonomy = generate_mock_16s_data(key)
            self.assertEqual(counts.shape, (24, 25))
            self.assertTrue(np.isfinite(counts.to_numpy()).all())
            result, groups = compute_differential_abundance(metadata, counts, taxonomy)
            self.assertEqual(len(result), 25)
            self.assertEqual(len(groups), 2)

class ImmuneReadOnlyTests(unittest.TestCase):
    def test_read_routes_and_missing_cell(self):
        from fastapi.testclient import TestClient
        spec = importlib.util.spec_from_file_location("immune_demo", ROOT / "apps/immune-app/main.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with TestClient(module.app) as client:
            for path in ["/", "/static/app.js", "/static/style.css", "/api/cells", "/api/scenarios", "/api/quiz"]:
                self.assertEqual(client.get(path).status_code, 200, path)
            self.assertEqual(client.get("/api/cells/not-a-cell").status_code, 404)
            self.assertEqual(client.post("/api/cells", json={}).status_code, 405)
            self.assertEqual(client.get("/static/../main.py").status_code, 404)

if __name__ == "__main__":
    unittest.main()
