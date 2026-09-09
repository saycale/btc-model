import math
import unittest

from audit import amplitudes, phi_at, plateau, saturation


class AuditReproductionTests(unittest.TestCase):
    def test_plateau_reference(self):
        self.assertAlmostEqual(plateau(1610), 657_000.0, places=6)

    def test_saturation_limits(self):
        self.assertAlmostEqual(float(saturation(1.0, 1_000_000.0)), 1.0, places=12)
        self.assertAlmostEqual(float(saturation(1e12, 657_000.0)), 657_000.0, places=6)

    def test_base_zeta_and_h5_amplitudes(self):
        zeta = 0.15 + 0.85 * phi_at((2029, 10), 1610, 1.897)
        self.assertAlmostEqual(zeta, 0.8697937616, places=9)
        a5, b5 = amplitudes(0.15, 0.50, 1610, 1.897)[5]
        self.assertAlmostEqual(a5, 0.0491868372, places=9)
        self.assertAlmostEqual(b5, -0.2413677688, places=9)

    def test_phi_is_bounded(self):
        for month in ((2025, 10), (2029, 10), (2033, 10), (2037, 10)):
            self.assertTrue(0.0 <= phi_at(month, 1610, 1.897) <= 1.0)


if __name__ == "__main__":
    unittest.main()
