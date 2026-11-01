"""Release-please must not create GitHub Releases; Release workflow is sole publisher.

Also locks the nonpublishing rehearsal contract: dry-run builds a synthetic
candidate with a local-only tag and cannot publish Releases or push tags.
Production publish still requires a GitHub-verified signed annotated tag.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RP = ROOT / ".github" / "workflows" / "release-please.yml"
REL = ROOT / ".github" / "workflows" / "release.yml"


class ReleasePublicationOwnershipTests(unittest.TestCase):
    def test_release_please_skips_github_release(self) -> None:
        text = RP.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^\s*skip-github-release:\s*true\s*$")

    def test_release_workflow_is_sole_github_release_creator(self) -> None:
        rp = RP.read_text(encoding="utf-8")
        rel = REL.read_text(encoding="utf-8")
        self.assertNotIn("gh release create", rp)
        self.assertIn("gh release create", rel)
        self.assertIn("workflow_dispatch", rel)
        self.assertIn("dry_run", rel)
        # Publish job must not run on dispatch dry-run
        self.assertIn("github.event_name == 'push'", rel)

    def test_signed_annotated_tag_gate_preserved(self) -> None:
        rel = REL.read_text(encoding="utf-8")
        self.assertIn("Verify signed annotated tag and version", rel)
        self.assertIn('verification"]["verified"]', rel)
        # Production path still rejects unverified tags (verified must equal true).
        self.assertIn('test "$verified" = "true"', rel)
        # Annotated-tag API path (lightweight tags fail here).
        self.assertIn("git/tags/", rel)

    def test_release_please_avoids_pat_secrets(self) -> None:
        text = RP.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"secrets\.[A-Z0-9_]*(TOKEN|PAT|APP)")

    def test_dry_run_uses_synthetic_rehearsal_fixture(self) -> None:
        rel = REL.read_text(encoding="utf-8")
        self.assertIn("Build nonpublishing rehearsal candidate", rel)
        self.assertIn("0.0.0-rehearsal.", rel)
        self.assertIn("M2M_REHEARSAL_VERSION", rel)
        self.assertIn("local only; never push", rel)
        # Dispatched rehearsals exercise the selected ref, not a hardcoded main checkout.
        self.assertIn("Checkout dispatched ref for nonpublishing dry-run", rel)
        self.assertIn("ref: ${{ github.ref }}", rel)
        self.assertNotIn("ref: main", rel.split("publish:")[0])

    def test_dry_run_cannot_publish_release_or_push_tags(self) -> None:
        rel = REL.read_text(encoding="utf-8")
        head, jobs = rel.split("\njobs:\n", 1)
        build, publish = jobs.split("\n  publish:\n", 1)
        self.assertIn("contents: read", head)
        self.assertNotIn("contents: write", build)
        self.assertNotIn("git push", build)
        self.assertNotIn("gh release create", build)
        # Publish remains push-of-tag only.
        self.assertIn("github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')", publish)
        self.assertIn("gh release create", publish)


if __name__ == "__main__":
    unittest.main()
