import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FrontendContractTests(unittest.TestCase):
    def test_scenario_state_behaviour(self):
        subprocess.run(["node", "audit/test_scenario.js"], cwd=ROOT, check=True)

    def test_pages_load_shared_assets_and_share_control(self):
        for name in ("index.html", "ru.html"):
            page = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn('GENERATED_RUNTIME_START', page)
            self.assertIn('window.BTC_MODEL_DATA', page)
            self.assertIn('id="share"', page)
            self.assertIn('id="g-unc"', page)
            self.assertIn("el('mb').value=initialScenario.b", page)
            self.assertNotIn("Object.entries(initialScenario)", page)

    def test_forecast_ledger_is_open_and_described(self):
        ledger = json.loads((ROOT / "data" / "forecast-ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger[0]["status"], "open")
        self.assertEqual(ledger[0]["claims"][0]["target"], "2029-10 H5 peak")

    def test_shared_core_is_executable(self):
        code = "global.window=global;global.location={href:'https://example.test/'};global.history={replaceState(){}};require('./model-core.js');const r=BTCModelCore.regress([1,2,3],[2,4,6]);if(Math.abs(r.b-2)>1e-9)process.exit(1);"
        subprocess.run(["node", "-e", code], cwd=ROOT, check=True)


if __name__ == "__main__":
    unittest.main()
