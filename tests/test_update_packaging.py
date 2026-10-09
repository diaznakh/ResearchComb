"""Keep the standalone update command and installed version consistent."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class UpdatePackaging(unittest.TestCase):
    def test_installed_version_matches_plugin_manifest(self):
        manifest = json.loads((ROOT / "plugin.json").read_text())
        installed = (ROOT / "skills/researchcomb/VERSION").read_text().strip()
        self.assertEqual(installed, manifest["version"])

    def test_update_check_is_separate_from_research_workflows(self):
        skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(skills), 14)
        for skill in skills:
            with self.subTest(skill=skill.parent.name):
                text = skill.read_text()
                self.assertNotIn("update-check.md", text)
                if skill.parent.name != "comb-update":
                    self.assertNotIn("raw.githubusercontent.com/diaznakh/ResearchComb/main/plugin.json", text)
        update = (ROOT / "skills/comb-update/SKILL.md").read_text()
        self.assertIn("https://raw.githubusercontent.com/diaznakh/ResearchComb/main/plugin.json", update)
        self.assertIn("researchcomb/VERSION", update)

    def test_marketplace_loads_plugin_from_pinned_checkout(self):
        marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(marketplace["plugins"][0]["source"], {"source": "local", "path": "./"})
        self.assertIn("--ref VERIFIED_COMMIT_SHA", (ROOT / "skills/comb-update/SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
