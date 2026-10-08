"""Keep update guidance reachable from every installed workflow."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class UpdatePackaging(unittest.TestCase):
    def test_installed_version_matches_plugin_manifest(self):
        manifest = json.loads((ROOT / "plugin.json").read_text())
        installed = (ROOT / "skills/researchcomb/VERSION").read_text().strip()
        self.assertEqual(installed, manifest["version"])

    def test_each_workflow_links_shared_update_check(self):
        skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(skills), 12)
        for skill in skills:
            with self.subTest(skill=skill.parent.name):
                link = ("references/update-check.md" if skill.parent.name == "researchcomb"
                        else "../researchcomb/references/update-check.md")
                self.assertIn(f"]({link})", skill.read_text())
                self.assertTrue((skill.parent / link).is_file())


if __name__ == "__main__":
    unittest.main()
