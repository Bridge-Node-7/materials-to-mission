from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

COVERAGE_FLOOR_PERCENT = 95.0
ALLOWED_PLATFORM_SKIPS = {
    "tests.test_cli_more.test_cli_package_rejects_symlink_without_traceback",
    "tests.test_release.test_release_rejects_public_symlink",
    "tests.test_release.test_release_ignores_symlink_inside_excluded_directory",
}
ALLOWED_SKIP_REASON = "symbolic links unavailable in this environment"


@dataclass(frozen=True)
class PytestSummary:
    tests: int
    failures: int
    errors: int
    skipped: int
    skipped_cases: tuple[tuple[str, str], ...]


def parse_pytest_junit(path: Path) -> PytestSummary:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    if not suites:
        raise ValueError("pytest JUnit report contains no testsuite")

    tests = failures = errors = skipped = 0
    skipped_cases: list[tuple[str, str]] = []
    for suite in suites:
        tests += int(suite.attrib.get("tests", "0"))
        failures += int(suite.attrib.get("failures", "0"))
        errors += int(suite.attrib.get("errors", "0"))
        skipped += int(suite.attrib.get("skipped", "0"))
        for case in suite.findall("testcase"):
            skipped_node = case.find("skipped")
            if skipped_node is None:
                continue
            identifier = f"{case.attrib.get('classname', '')}.{case.attrib.get('name', '')}".strip(".")
            reason = (skipped_node.attrib.get("message") or skipped_node.text or "").strip()
            skipped_cases.append((identifier, reason))

    return PytestSummary(
        tests=tests,
        failures=failures,
        errors=errors,
        skipped=skipped,
        skipped_cases=tuple(skipped_cases),
    )


def validate_pytest_summary(summary: PytestSummary) -> None:
    if summary.failures or summary.errors:
        raise ValueError(
            f"pytest failures or errors detected: failures={summary.failures}, errors={summary.errors}"
        )
    if summary.skipped != len(summary.skipped_cases):
        raise ValueError("pytest skipped count does not match recorded skipped cases")
    for identifier, reason in summary.skipped_cases:
        if identifier not in ALLOWED_PLATFORM_SKIPS or ALLOWED_SKIP_REASON not in reason:
            raise ValueError(f"unexpected skipped test: {identifier}: {reason}")


def render_validation_report(
    test_count: int,
    version: str,
    validation_profile: str = "unspecified",
) -> str:
    version = version.strip()
    if not version:
        raise ValueError("project version is required")
    validation_profile = validation_profile.strip()
    if not validation_profile:
        raise ValueError("validation profile is required")
    report = f"""# Validation Report

**Project:** Materials-to-Mission
**Version:** {version}
**Validation profile:** {validation_profile}
**Status:** PASS within the stated public synthetic scope

## Executed

- Python compilation: PASS
- JSON parsing: PASS
- JSON Schema validation: PASS
- Semantic validation: PASS
- Public-boundary validation: PASS
- Adversarial fixtures: PASS
- Unit and integration tests: {test_count} collected; all runnable tests PASS
- Platform-dependent test policy: only the three documented symlink-unavailable cases may skip
- Combined statement and branch coverage: PASS at or above the 95 percent floor
- Markdown relative links: PASS
- GitHub Actions full-SHA pinning: PASS
- Public-source maintainer gate contracts: PASS
- Hosted Release workflow contract: PASS
- Separate publication-kit gates: validated by the publication kit
- Symbolic-link rejection: PASS
- Deterministic archive comparison: PASS
- Checked-in validation evidence: current and host-independent
- SHA-256 manifest verification: PASS
- Compressed-data integrity: verified by the release build

## Not Proven

This validation does not prove a real material, supplier, laboratory, sample,
lot, mission, legal, regulatory, certification, qualification, production,
customer, government, or commercial conclusion.
"""
    return "\n".join(line.rstrip(" \t") for line in report.splitlines()) + "\n"
