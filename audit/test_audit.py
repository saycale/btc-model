import math
import re
import unittest
from pathlib import Path

from audit import B_REF, OBS, OBS_LAST_DATE, amplitudes, phi_at, plateau, saturation


class AuditReproductionTests(unittest.TestCase):
    def test_plateau_reference(self):
        self.assertAlmostEqual(plateau(1610), 657_000.0, places=6)

    def test_saturation_limits(self):
        self.assertAlmostEqual(float(saturation(1.0, 1_000_000.0)), 1.0, places=12)
        self.assertAlmostEqual(float(saturation(1e12, 657_000.0)), 657_000.0, places=6)

    def test_base_zeta_and_h5_amplitudes(self):
        zeta = 0.15 + 0.85 * phi_at((2029, 10), 1610, B_REF)
        a5, b5 = amplitudes(0.15, 0.50, 1610, B_REF)[5]
        self.assertAlmostEqual(a5, (0.030 + 0.15 * (0.207 - 0.030)) * zeta, places=9)
        self.assertAlmostEqual(b5, -0.37 * 0.75 * zeta, places=9)

    def test_current_provisional_observation(self):
        self.assertEqual(OBS_LAST_DATE, (2026, 9, 9))
        self.assertEqual(len(OBS), 195)
        self.assertAlmostEqual(float(OBS[-1]), 78_587.0)

    def test_dynamic_reference_fit(self):
        self.assertAlmostEqual(B_REF, 1.8799811585, places=9)

    def test_english_and_russian_samples_match(self):
        root = Path(__file__).resolve().parents[1]
        pages = [(root / name).read_text(encoding="utf-8") for name in ("index.html", "ru.html")]
        arrays = [re.search(r"const\s+OBS\s*=\s*\[(.*?)\];", page, re.S).group(1) for page in pages]
        dates = [re.search(r"const\s+OBS_LAST_DATE\s*=\s*\[(.*?)\]", page).group(1) for page in pages]
        self.assertEqual(arrays[0], arrays[1])
        self.assertEqual(dates[0], dates[1])

    def test_phi_is_bounded(self):
        for month in ((2025, 10), (2029, 10), (2033, 10), (2037, 10)):
            self.assertTrue(0.0 <= phi_at(month, 1610, B_REF) <= 1.0)


if __name__ == "__main__":
    unittest.main()
