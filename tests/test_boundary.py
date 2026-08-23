from materials_to_mission.boundary import scan_public_boundary


def test_clean_example_has_no_boundary_findings(example_case):
    assert scan_public_boundary(example_case) == []


def test_secret_like_pattern_is_detected(example_case):
    example_case["secret"] = "api_key = ABC123"
    findings = scan_public_boundary(example_case)
    assert any("pattern" in item for item in findings)



def test_compound_secret_key_names_are_detected(example_case):
    for key in (
        "github_token",
        "db_password",
        "service_client_secret",
        "aws_access_key",
        "ssh_private_key",
        "x_api_key",
    ):
        candidate = dict(example_case)
        candidate[key] = "placeholder"
        findings = scan_public_boundary(candidate)
        assert any("prohibited public key" in item for item in findings), key


def test_credential_shaped_values_are_detected(example_case):
    # Build samples at runtime so repository history never stores a
    # credential-shaped literal while still exercising each detector.
    samples = (
        "".join(("AK", "IA", "IOSFODNN7EXAMPLE")),
        "".join(("gh", "p_", "abcdefghijklmnopqrstuvwxyz1234567890")),
        "".join(("AI", "zaSyA12345678901234567890123456789012")),
        "".join(("xo", "xb-", "1234567890-", "abcdefghijklmnop")),
    )
    for sample in samples:
        candidate = dict(example_case)
        candidate["notes"] = sample
        findings = scan_public_boundary(candidate)
        assert any("credential-shaped" in item for item in findings), sample


def test_unicode_confusable_smuggling_is_detected(example_case):
    candidate = dict(example_case)
    candidate["notes"] = "claѕѕified"  # Cyrillic small dze U+0455 for both s characters.
    findings = scan_public_boundary(candidate)
    assert any("classified" in item for item in findings)
