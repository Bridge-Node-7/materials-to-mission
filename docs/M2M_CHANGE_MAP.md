# Materials-to-Mission Reference Baseline Change Map

Generated:
Thu Aug 20 08:43:18 UTC 2026

## Baseline

Commit:
f141a85cee9615a57582855e677450af7584cfd4

Version:
0.7.4

## Targeted Review Areas

### Search: BN7-specific

./public-snapshots/material-systems/YIG-001/pathway.json:96:      "summary": "Public evidence reviewed here does not establish BN7-specific qualified precursor form, purity, processor, substrate lot, repeatability, or assured supply for a mission-relevant YIG stack.",
./public-snapshots/material-systems/YIG-001/pathway.json:101:      "evidence_basis": "No qualifying public evidence was identified in the reviewed corpus for a BN7-specific precursor form, purity, processor, substrate lot, repeatability, or assured mission-relevant YIG material stack."

### Search: mission-specific

./public-snapshots/gallium/GA-001/public-view.json:14:    "No supplier, customer, lot, facility, qualification, acquisition, or mission-specific evidence is asserted.",
./public-snapshots/material-systems/YIG-001/pathway.json:141:      "evidence_basis": "The reviewed literature identifies relevant material and substrate performance variables, but it does not provide a BN7 mission-specific acceptance range, independent qualification protocol, repeatability baseline, or production-yield criterion."
./public-snapshots/material-systems/YIG-001/pathway.json:158:      "evidence_basis": "No mission-specific public evidence was identified in the reviewed corpus for availability, sustainment, security, reliability, or operational performance.",
./public-snapshots/material-systems/YIG-001/pathway.json:204:    "Only then evaluate acquisition, integration, sustainment, and mission-specific acceptance."

### Search: currently

./public-snapshots/gallium/GA-001/README.md:38:recovery work. It does not establish that the resulting material is currently qualified,
./scripts/build_web.py:411:        f'<p>{len(selected_pathways)} public examples currently shared with deeper reviewed context. Reviewed does not mean qualified.</p></header>'

### Search: Current page

./scripts/build_web.py:619:        f'<small>{esc(source.get("source_date") or "Current page")} · verified {esc(source["verified_at"])}</small>'

### Search: m0-strict

./.github/workflows/ci.yml:45:            --profile m0-strict-0.4.0 \
./.github/workflows/ci.yml:54:          assert data["validation_profile"] == "m0-strict-0.4.0"
./CHANGELOG.md:92:- Clarified the historical `m0-strict-0.2.0` value as the **GA-001 snapshot validation profile** while retaining `m0-strict-0.4.0` as the current default profile.
./CHANGELOG.md:160:- Restored `m0-strict-0.2.0` to its released accept/reject behavior for the automation-owner aliases introduced during v0.3.1 maintenance.
./CHANGELOG.md:161:- Added `m0-strict-0.4.0` as the explicitly versioned profile carrying rejection for `Scoring Engine`, `Rules Engine`, and `Inference Service`.
./CHANGELOG.md:162:- Made `m0-strict-0.4.0` the default profile for new validation while preserving explicit historical evaluation under earlier profiles.
./CHANGELOG.md:167:- `m0-baseline-0.1.0` behavior and released `m0-strict-0.2.0` behavior.
./CHANGELOG.md:209:- Validation profiles remain `m0-baseline-0.1.0` and `m0-strict-0.2.0`.
./CHANGELOG.md:219:- Default `m0-strict-0.2.0` strengthened M0 behavior.
./docs/FIVE_MINUTE_EVALUATION.md:19:m2m validate examples/synthetic-critical-material-pathway/case.json --public --profile m0-strict-0.4.0
./docs/FIVE_MINUTE_EVALUATION.md:31:m2m render examples/synthetic-critical-material-pathway/case.json --output build/decision-passport.md --profile m0-strict-0.4.0
./docs/FIVE_MINUTE_EVALUATION.md:40:m2m validate examples/invalid/missing-human-owner.json --public --json --profile m0-strict-0.4.0
./docs/INTEROPERABILITY.md:14:Validation consumers must preserve the distinction between structural schema identity and semantic validation-profile identity. Canonical records remain bound to the immutable v0.1.0 schemas, while semantic acceptance is evaluated under an explicit profile such as `m0-baseline-0.1.0` or `m0-strict-0.2.0`. A consumer must not infer a validation profile solely from `schema_version`.
./docs/VALIDATION.md:52:Semantic validation is explicitly versioned independently from the immutable v0.1.0 JSON Schema authority. The default profile is `m0-strict-0.2.0`. Historical v0.1.0 compatibility is available through `m0-baseline-0.1.0`. The complete maintainer gate verifies the default profile recorded by the toolkit, `PROJECT_FACTS.json`, and generated validation evidence.
VALIDATION_PROFILES.md:16:## `m0-strict-0.2.0`
VALIDATION_PROFILES.md:21:## `m0-strict-0.4.0`
VALIDATION_PROFILES.md:23:Default M0 strict profile for v0.4.0. It preserves the `m0-strict-0.2.0` semantic rules and
VALIDATION_PROFILES.md:36:m2m validate case.json --public --profile m0-strict-0.4.0
VALIDATION_PROFILES.md:37:m2m validate strict-compatibility.json --public --profile m0-strict-0.2.0
VALIDATION_PROFILES.md:41:If `--profile` is omitted, the documented default is `m0-strict-0.4.0`.
./PROJECT_FACTS.json:98:  "validation_profile_default": "m0-strict-0.4.0",
./PROJECT_FACTS.json:102:    "m0-strict-0.2.0",
./PROJECT_FACTS.json:103:    "m0-strict-0.4.0"
./public-snapshots/gallium/GA-001/public-view.json:115:  "validation_profile": "m0-strict-0.2.0",
./scripts/evaluate_public_method.py:13:PROFILE = "m0-strict-0.2.0"
./src/materials_to_mission/validation_profiles.py:6:STRICT_PROFILE_ID = "m0-strict-0.2.0"
./src/materials_to_mission/validation_profiles.py:7:STRICT_V040_PROFILE_ID = "m0-strict-0.4.0"
./tests/test_consumer_integrity_v020.py:36:    assert STRICT_PROFILE_ID == "m0-strict-0.2.0"
./tests/test_consumer_integrity_v020.py:37:    assert STRICT_V040_PROFILE_ID == "m0-strict-0.4.0"
./tests/test_v060_ux_contract.py:42:    assert snap['human_authority_required'] is True and view['validation_profile']=='m0-strict-0.2.0'
./VALIDATION_REPORT.md:5:**Validation profile:** m0-strict-0.4.0
./VERSIONING.md:28:- `m0-strict-0.2.0` — released strengthened M0 compatibility profile.
./VERSIONING.md:29:- `m0-strict-0.4.0` — current M0 strict profile with explicitly versioned automation-authority alias rejection.
./VERSIONING.md:31:The toolkit default is `m0-strict-0.4.0`. Released earlier profiles remain behaviorally available under their explicit identifiers, and the applied profile is surfaced in machine-readable validation output and checked-in validation evidence.

### Search: GA-001

./CHANGELOG.md:18:- Frozen GA-001, MF-001, and YIG-001 evidence.
./CHANGELOG.md:31:- Preserved frozen GA-001, MF-001, and YIG-001 evidence, M0 maturity, visible unknowns, and human consequential authority.
./CHANGELOG.md:43:- Preserved exactly two Selected Pathways, frozen GA-001/MF-001/YIG-001 evidence, M0 maturity, and human consequential authority.
./CHANGELOG.md:53:- Preserved the accepted Atlas journey, exactly two selected pathways, frozen GA-001/MF-001/YIG-001 evidence, M0 maturity, fail-closed unknowns, and human consequential authority.
./CHANGELOG.md:69:- Frozen GA-001, MF-001, and YIG-001 evidence is unchanged. M0 remains M0.
./CHANGELOG.md:82:- Preserved the exact USGS 2025 60-mineral field, 15 rare earth elements, frozen GA-001 v1.0.0 evidence, YIG engineered-system classification, M0 maturity, unknown-as-non-favorable semantics, and human consequential authority.
./CHANGELOG.md:90:- Made all seven GA-001 claim source references navigate to the dedicated controlled GA-001 source registry and authoritative USGS/DOE URLs.
./CHANGELOG.md:91:- Kept general Materials Field Sources and GA-001 Reviewed Sources visibly separate without aliasing identifiers or normalizing distinct source dates.
./CHANGELOG.md:92:- Clarified the historical `m0-strict-0.2.0` value as the **GA-001 snapshot validation profile** while retaining `m0-strict-0.4.0` as the current default profile.
./CHANGELOG.md:97:- Preserved the exact 60-mineral USGS 2025 field, 15 rare earth elements, frozen GA-001 v1.0.0 evidence, YIG engineered-system classification, no-score behavior, public/private boundary, and canonical v0.1.0 schema authority.
./CHANGELOG.md:103:- Preserved GA-001 evidence meaning, schema authority, M0 maturity, and human consequential authority.
./CHANGELOG.md:121:- Gallium GA-001 and bounded YIG-001 evidence meaning.
./CHANGELOG.md:136:- Gallium GA-001 as the only released Reviewed Pathway and YIG-001 as bounded Reviewed Public Context.
./CHANGELOG.md:150:- Gallium GA-001 as the only released Reviewed Pathway.
./CHANGELOG.md:168:- Frozen GA-001 v1.0.0 evidence and public-view contract 0.3.0.
./CHANGELOG.md:187:- Frozen GA-001 v1.0.0 snapshot/source/rights evidence.
./CHANGELOG.md:194:- Frozen GA-001 v1.0.0 Gallium public-source evidence snapshot and source-support view.
./CHANGELOG.md:210:- GA-001 is a public-source evidence snapshot, not a real operational Case 001.
./docs/START_HERE.md:21:The synthetic reference case teaches structure only. GA-001 is separately identified as a bounded reviewed public-source snapshot.
./PROJECT_FACTS.json:42:  "gallium_public_snapshot_status": "frozen-ga-001-v1.0.0",
./PROJECT_FACTS.json:44:  "gallium_snapshot_path": "public-snapshots/gallium/GA-001/snapshot.json",
./public-snapshots/gallium/GA-001/public-view.json:21:  "source_reference": "public-snapshots/gallium/GA-001/snapshot.json",
./public-snapshots/gallium/GA-001/README.md:1:# GA-001 — Gallium Public-Source Evidence Snapshot
./public-snapshots/gallium/GA-001/README.md:8:GA-001 demonstrates the Materials-to-Mission method against bounded public evidence. It is
./public-snapshots/gallium/GA-001/README.md:26:GA-001 uses only official U.S. Government sources for v1.0.0:
./public-snapshots/gallium/GA-001/rights.json:6:  "review_rule": "GA-001 stores official-source URLs, bibliographic metadata, and original structured paraphrases. It does not archive source webpages, PDFs, photographs, or other source-agency media.",
./public-snapshots/gallium/GA-001/rights.json:9:  "snapshot_id": "GA-001",
./public-snapshots/gallium/GA-001/snapshot.json:106:  "snapshot_id": "GA-001",
./public-snapshots/gallium/GA-001/source-register.json:3:  "snapshot_id": "GA-001",
./public-snapshots/gallium/GA-001/source-register.json:4:  "source_policy": "Official U.S. Government public sources only for GA-001 v1.0.0. Repository content stores source metadata and original paraphrase, not copied source bodies.",
./public-snapshots/material-systems/YIG-001/README.md:5:It is intentionally distinct from GA-001:
./public-snapshots/material-systems/YIG-001/README.md:6:- GA-001 is the released Gallium Reviewed Pathway.
./public-snapshots/materials-field/MF-001/atlas.json:318:        "snapshot_id": "GA-001"
./public-snapshots/materials-field/MF-001/public-forms.json:17:        "GA-001"
./public-snapshots/materials-field/MF-001/public-forms.json:37:        "GA-001"
./public-snapshots/materials-field/MF-001/public-forms.json:53:        "GA-001"
./public-snapshots/materials-field/MF-001/README.md:12:MF-001 does not claim that all 60 minerals have a reviewed Materials-to-Mission pathway. Gallium remains the only material in this release with a released reviewed pathway through GA-001.
./public-snapshots/materials-field/MF-001/source-register.json:4:  "source_policy": "Official U.S. Government public sources control official designation, application mapping, commodity and policy context. GA-001 remains the separately governed Bridge Node 7 reviewed public-source snapshot for Gallium.",
./public-snapshots/materials-field/MF-001/source-register.json:49:      "source_id": "GA-001",
./public-snapshots/materials-field/MF-001/source-register.json:52:      "title": "GA-001 v1.0.0 Reviewed Public-Source Evidence Snapshot",
./public-snapshots/materials-field/MF-001/source-register.json:55:      "url": "https://github.com/Bridge-Node-7/materials-to-mission/tree/v0.4.0/public-snapshots/gallium/GA-001",
./README.md:22:- Inspect Gallium GA-001 as a bounded reviewed public-source pathway.
./README.md:61:**GA-001** is a reviewed public-source Gallium evidence snapshot based on official public sources and original paraphrase. It is not a real operational Case 001 and does not imply qualification, acquisition approval, mission readiness, adoption, or commercial validation.
./RELEASE_NOTES.md:17:- Frozen GA-001 v1.0.0, MF-001, and YIG-001 evidence is unchanged.
./REPO_FILE_MANIFEST.sha256:62:4509bff67b2c23ead90fd7520a757575426b2fefd5aa2a7ecf63f410c4475834  public-snapshots/gallium/GA-001/README.md
./REPO_FILE_MANIFEST.sha256:63:31bdbf1a074e1f838205eab16c32ee02b8e3ee1a75899d0e476db0ce9fdf8676  public-snapshots/gallium/GA-001/public-view.json
./REPO_FILE_MANIFEST.sha256:64:e289a7a9669a47b1936f1f809216d4de216c2e72d48f51f7769ec8ef9f1cc848  public-snapshots/gallium/GA-001/rights.json
./REPO_FILE_MANIFEST.sha256:65:6e100f9e1c3bac48fa93ee7b0838c117e8e67313fa0540f918058eec7ea0e968  public-snapshots/gallium/GA-001/snapshot.json
./REPO_FILE_MANIFEST.sha256:66:13685720de8f18c0b19fb937e1733295b0950ad487ddde8fe452bb92b9514787  public-snapshots/gallium/GA-001/source-register.json
./scripts/build_web.py:17:GA001 = ROOT / "public-snapshots/gallium/GA-001"
./scripts/build_web.py:99:    if snapshot.get("snapshot_id") != "GA-001" or snapshot.get("snapshot_version") != "1.0.0":
./scripts/build_web.py:102:        raise SystemExit("STOP - GA-001 public-view source kind changed")
./scripts/build_web.py:106:        raise SystemExit("STOP - GA-001 rights posture changed")
./scripts/build_web.py:108:        raise SystemExit("STOP - GA-001 public rights approval changed")
./scripts/build_web.py:111:    unique(ga_sources, "source_id", "GA-001 source ID")
./scripts/build_web.py:115:            raise SystemExit("STOP - GA-001 source authority changed")
./scripts/build_web.py:118:            raise SystemExit("STOP - GA-001 source host/scheme changed")
./scripts/build_web.py:122:    unique(claims, "claim_id", "GA-001 claim ID")
./scripts/build_web.py:126:            raise SystemExit("STOP - invalid GA-001 claim state")
./scripts/build_web.py:129:            raise SystemExit("STOP - unresolved GA-001 claim source")
./scripts/build_web.py:132:    unique(support, "id", "GA-001 support ID")
./scripts/build_web.py:140:    unique(interpretations, "interpretation_id", "GA-001 interpretation ID")
./scripts/build_web.py:199:    if [(m["name"], m["review"].get("snapshot_id")) for m in reviewed] != [("Gallium", "GA-001")]:
./scripts/build_web.py:289:            source_ids.extend(["DOE-TRACE-GA-2026", "GA-001"])
./scripts/build_web.py:481:            raise SystemExit("STOP - unresolved GA-001 claim source during render")
./scripts/build_web.py:505:            f'<div><span>GA-001 snapshot validation profile</span><b>{esc(view["validation_profile"])}</b></div>'
./tests/test_foundation_hardening.py:60:        assert pathway["record_id"] in {"GA-001", "YIG-001"}
./tests/test_ga001_public_snapshot.py:10:BASE = ROOT / "public-snapshots" / "gallium" / "GA-001"
./tests/test_ga001_public_snapshot.py:19:    assert snapshot["snapshot_id"] == "GA-001"
./tests/test_materials_atlas_r6.py:18:    assert [(material["name"], material["review"]["snapshot_id"]) for material in reviewed] == [("Gallium", "GA-001")]
./tests/test_public_visual_contract.py:37:    assert facts["gallium_public_snapshot_status"] == "frozen-ga-001-v1.0.0"
./tests/test_uxf_v031.py:25:    view = json.loads((ROOT / "public-snapshots/gallium/GA-001/public-view.json").read_text(encoding="utf-8"))
./tests/test_v060_ux_contract.py:16:    assert 'GA-001 snapshot validation profile' in html
./tests/test_v060_ux_contract.py:19:    assert 'Materials Field Sources' in html and 'GA-001 Reviewed Sources' in html
./tests/test_v060_ux_contract.py:28:    ga=json.loads((ROOT/'public-snapshots/gallium/GA-001/source-register.json').read_text(encoding='utf-8'))
./tests/test_v060_ux_contract.py:38:    snap=json.loads((ROOT/'public-snapshots/gallium/GA-001/snapshot.json').read_text(encoding='utf-8'))
./tests/test_v060_ux_contract.py:39:    view=json.loads((ROOT/'public-snapshots/gallium/GA-001/public-view.json').read_text(encoding='utf-8'))
./tests/test_v060_ux_contract.py:40:    assert snap['snapshot_id']=='GA-001' and snap['snapshot_version']=='1.0.0'
./tests/test_v061_truth_accessibility.py:69:    for token in ('Frozen GA-001 v1.0.0','YIG remains an engineered material system','M0','Human consequential authority'):
./tests/test_v070_selected_pathways_release.py:10:    assert 'Frozen GA-001, MF-001, and YIG-001 evidence is unchanged' in changelog
./tests/test_v072_corrective_maintenance.py:69:    assert {item["record_id"] for item in registry["pathways"]} == {"GA-001", "YIG-001"}
./web/index.html:163:    <article><span>Evidence review</span><strong>Reviewed Pathway · GA-001</strong></article>
./web/index.html:193:    <summary><span>Reviewed Gallium claim register</span><small>7 source-linked claims · GA-001</small></summary>
./web/index.html:232:  <div class="source-family ga-source-family"><p class="eyebrow">REVIEWED EVIDENCE</p><h3>GA-001 Reviewed Sources</h3><div class="ga-source-grid"><!-- R6:GA_SOURCES --></div></div>
./web/selected-pathways.json:6:      "record_id": "GA-001",

### Search: validation profile

./CHANGELOG.md:92:- Clarified the historical `m0-strict-0.2.0` value as the **GA-001 snapshot validation profile** while retaining `m0-strict-0.4.0` as the current default profile.
./CHANGELOG.md:209:- Validation profiles remain `m0-baseline-0.1.0` and `m0-strict-0.2.0`.
./CHANGELOG.md:240:Candidate 0.2.0 resolves that ambiguity by keeping schema authority unchanged while versioning semantic acceptance behavior explicitly through validation profiles.
./docs/INTEROPERABILITY.md:14:Validation consumers must preserve the distinction between structural schema identity and semantic validation-profile identity. Canonical records remain bound to the immutable v0.1.0 schemas, while semantic acceptance is evaluated under an explicit profile such as `m0-baseline-0.1.0` or `m0-strict-0.2.0`. A consumer must not infer a validation profile solely from `schema_version`.
./docs/VALIDATION.md:50:## Validation Profiles
VALIDATION_PROFILES.md:1:# Validation Profiles
VALIDATION_PROFILES.md:3:Validation profiles version semantic acceptance behavior independently from the immutable
VALIDATION_PROFILES.md:29:Released validation profiles are behavioral contracts. A released profile does not silently
VALIDATION_PROFILES.md:46:A validation profile governs automated structural and declared semantic findings. It does
./README.md:87:- Validation Profiles (Validation Profiles artifact)
./scripts/build_web.py:505:            f'<div><span>GA-001 snapshot validation profile</span><b>{esc(view["validation_profile"])}</b></div>'
./scripts/check_repo.py:224:            "STOP - PROJECT_FACTS.json default validation profile differs "
./scripts/evaluate_public_method.py:62:        return stop("invalid fixture did not report the explicit validation profile", invalid)
./src/materials_to_mission/cli.py:80:        help=f"semantic validation profile; default: {DEFAULT_VALIDATION_PROFILE}",
./src/materials_to_mission/cli.py:95:        help=f"semantic validation profile; default: {DEFAULT_VALIDATION_PROFILE}",
./src/materials_to_mission/validation_evidence.py:77:        raise ValueError("validation profile is required")
./src/materials_to_mission/validation_evidence.py:82:**Validation profile:** {validation_profile}
./src/materials_to_mission/validation_profiles.py:46:        raise ValueError(f"unknown validation profile: {profile_id}") from None
./src/materials_to_mission/validator.py:691:                f"unsupported validation profile: {resolved.profile_id}"
./tests/test_consumer_integrity_v020.py:42:    with pytest.raises(ValueError, match="unknown validation profile"):
./tests/test_consumer_integrity_v020.py:232:    assert f"**Validation profile:** {STRICT_PROFILE_ID}" in report
./tests/test_v060_ux_contract.py:16:    assert 'GA-001 snapshot validation profile' in html
./VALIDATION_REPORT.md:5:**Validation profile:** m0-strict-0.4.0
./VERSIONING.md:8:2. **Validation profile** identifies semantic rules and finding severities.
./VERSIONING.md:17:The existing `v0.1.0` schema identifiers remain immutable. Validation profiles do not add a required field to those schemas.
./VERSIONING.md:21:Released validation profiles are behavioral contracts with explicit compatibility corpora. A patch may repair an implementation defect only when the released profile's declared accept/reject behavior remains intact. A new ERROR-level semantic requirement, changed rejection criterion, or severity promotion to ERROR requires a new validation-profile identifier.

## Existing Architecture


Existing systems identified:

- Evidence model
- Validation profiles
- AI provenance
- Decision Passport
- Material Assurance Record
- Synthetic examples
- Browser UAT
- Release validation

Principle:

Extend existing truth.
Do not create duplicate systems.

