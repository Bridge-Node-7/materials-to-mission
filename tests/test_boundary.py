from materials_to_mission.boundary import scan_public_boundary


def test_clean_example_has_no_boundary_findings(example_case):
    assert scan_public_boundary(example_case) == []


def test_secret_like_pattern_is_detected(example_case):
    example_case["secret"] = "api_key = ABC123"
    findings = scan_public_boundary(example_case)
    assert any("pattern" in item for item in findings)
