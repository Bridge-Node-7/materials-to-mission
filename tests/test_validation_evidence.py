from pathlib import Path

import pytest

from materials_to_mission.validation_evidence import (
    PytestSummary,
    render_validation_report,
    parse_pytest_junit,
    validate_pytest_summary,
)


def test_validation_report_is_host_independent():
    windows_like = render_validation_report(test_count=226, version="0.6.0")
    linux_like = render_validation_report(test_count=227, version="0.6.0")
    assert windows_like == linux_like
    assert "Unit and integration tests: all runnable tests PASS" in windows_like
    assert "226 collected" not in windows_like
    assert "227 collected" not in windows_like
    assert "95 percent floor" in windows_like
    assert "96.88" not in windows_like
    assert "96.40" not in windows_like

def test_parse_and_validate_junit_without_skips(tmp_path: Path):
    path = tmp_path / "pytest.xml"
    path.write_text(
        '<testsuite tests="2" failures="0" errors="0" skipped="0">'
        '<testcase classname="tests.test_one" name="test_a" />'
        '<testcase classname="tests.test_one" name="test_b" />'
        '</testsuite>',
        encoding="utf-8",
    )
    summary = parse_pytest_junit(path)
    assert summary.tests == 2
    validate_pytest_summary(summary)


def test_documented_platform_symlink_skip_is_allowed():
    summary = PytestSummary(
        tests=1,
        failures=0,
        errors=0,
        skipped=1,
        skipped_cases=((
            "tests.test_release.test_release_rejects_public_symlink",
            "symbolic links unavailable in this environment",
        ),),
    )
    validate_pytest_summary(summary)


def test_unexpected_skip_is_rejected():
    summary = PytestSummary(
        tests=1,
        failures=0,
        errors=0,
        skipped=1,
        skipped_cases=(("tests.test_other.test_unrelated", "not available"),),
    )
    with pytest.raises(ValueError, match="unexpected skipped test"):
        validate_pytest_summary(summary)


def test_parse_junit_with_allowed_skip(tmp_path: Path):
    path = tmp_path / "pytest.xml"
    path.write_text(
        '<testsuites><testsuite tests="1" failures="0" errors="0" skipped="1">'
        '<testcase classname="tests.test_release" name="test_release_rejects_public_symlink">'
        '<skipped message="symbolic links unavailable in this environment" />'
        '</testcase></testsuite></testsuites>',
        encoding="utf-8",
    )
    summary = parse_pytest_junit(path)
    assert summary.skipped == 1
    validate_pytest_summary(summary)


def test_parse_junit_rejects_missing_suite(tmp_path: Path):
    path = tmp_path / "pytest.xml"
    path.write_text('<not-tests />', encoding="utf-8")
    with pytest.raises(ValueError, match="contains no testsuite"):
        parse_pytest_junit(path)


def test_validate_rejects_failures_and_errors():
    summary = PytestSummary(
        tests=2,
        failures=1,
        errors=1,
        skipped=0,
        skipped_cases=(),
    )
    with pytest.raises(ValueError, match="failures or errors"):
        validate_pytest_summary(summary)


def test_validate_rejects_skipped_count_mismatch():
    summary = PytestSummary(
        tests=1,
        failures=0,
        errors=0,
        skipped=1,
        skipped_cases=(),
    )
    with pytest.raises(ValueError, match="skipped count"):
        validate_pytest_summary(summary)

def test_validation_report_requires_project_version():
    with pytest.raises(ValueError, match="project version is required"):
        render_validation_report(70, " ")

def test_validation_report_has_no_trailing_whitespace():
    report = render_validation_report(70, "0.1.2")
    assert all(
        line == line.rstrip(" \t")
        for line in report.splitlines()
    )
