from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_visual_contract_preserves_bridge_node_7_family() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
    assert "Materials-to-Mission Atlas" in html
    assert "Evidence-First. Mission-Aligned." in html
    assert "Beyond the Evidence Map" in html
    assert "Explore the Decision Experience" in html
    assert "Human decision authority remains required." in html
    assert (
        "This map organizes public evidence and unresolved questions. It does not approve, qualify, "
        "or certify a pathway. Decisions requiring judgment remain with responsible people and organizations."
    ) in html
    assert "--bg:#020712" in css.replace(" ", "")
    assert "--gold:#e7ba52" in css.replace(" ", "")
    assert "background:#f7f3e8" not in css.lower()
    assert "background:#faf7ef" not in css.lower()

def test_first_surface_is_visual_not_explanatory_prose_wall() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    before_trace = html.split('id="trace"', 1)[0]
    assert before_trace.count("<h1") == 1
    assert "Materials-to-Mission Atlas" in before_trace
    assert before_trace.count('class="mineral') == 0  # generated at build-time, not hardcoded truth

def test_mobile_precision_modes_exist() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
    assert 'id="indexView"' in html
    assert 'id="globalSearch"' in html
    assert "overflow-x:auto" in css.replace(" ", "")
    assert "min-width:820px" in css.replace(" ", "")
