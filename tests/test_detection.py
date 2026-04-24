from __future__ import annotations

from pathlib import Path
import sys
import unittest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hellosearch_runtime.detection import detect_runtime_environment


class DetectionTests(unittest.TestCase):
    def test_detect_runtime_environment_returns_workspace_root(self):
        report = detect_runtime_environment(Path("D:/GitHub/dev/hellosearch"))
        self.assertEqual(str(report.workspace_root), "D:\\GitHub\\dev")
        self.assertTrue(report.primary_runtime is not None)


if __name__ == "__main__":
    unittest.main()
