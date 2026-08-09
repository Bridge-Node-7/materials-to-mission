from materials_to_mission.report import render_decision_passport


def test_report_is_deterministic(example_case):
    first = render_decision_passport(example_case)
    second = render_decision_passport(example_case)
    assert first == second


def test_report_contains_required_sections(example_case):
    report = render_decision_passport(example_case)
    for heading in ["# Fictional Precision Actuator Material Pathway: Decision Passport", "## Evidence Posture", "## Critical Conditions", "## Recommendation", "## Stop Rule", "## Limitations"]:
        assert heading in report
    assert "Fictional Human Decision Owner" in report
    assert "`HOLD`" in report
