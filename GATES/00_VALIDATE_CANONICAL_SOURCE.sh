#!/usr/bin/env bash
bn7_m2m_validate_canonical_source(){
  set -Eeuo pipefail
  local ROOT='' EVIDENCE='' VENV='' PY='' RC=0

  printf '%s\n' 'WAIT - MATERIALS-TO-MISSION CANONICAL SOURCE VALIDATION'
  printf '%s\n' 'BOUNDARY - isolated local validation and deterministic packaging only; no GitHub read or write'
  for cmd in python3 sha256sum unzip bash; do
    command -v "$cmd" >/dev/null 2>&1 || { printf 'STOP - missing command: %s\n' "$cmd"; return 20; }
  done

  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  EVIDENCE="$HOME/BN7_M2M_EVIDENCE/SOURCE_$(date -u +%Y%m%dT%H%M%SZ)_$RANDOM"
  VENV="$EVIDENCE/venv"
  mkdir -p "$EVIDENCE" || return 20

  printf 'WORKING - source: %s\n' "$ROOT"
  printf 'WORKING - evidence: %s\n' "$EVIDENCE"

  {
    python3 -m venv "$VENV" || RC=$?
    if (( RC == 0 )); then
      PY="$VENV/bin/python"
      [[ -x "$PY" ]] || PY="$VENV/Scripts/python.exe"
      [[ -x "$PY" ]] || RC=20
    fi
    (( RC == 0 )) && "$PY" -m pip install -r "$ROOT/requirements-dev.lock" || RC=$?
    (( RC == 0 )) && "$PY" -m pip install --no-deps --no-build-isolation -e "$ROOT" || RC=$?
    (( RC == 0 )) && (cd "$ROOT" && "$PY" scripts/check_repo.py) || RC=$?
  } > >(tee "$EVIDENCE/validation.log") 2>&1

  if (( RC != 0 )); then
    printf 'STOP - canonical source validation failed; evidence preserved at %s\n' "$EVIDENCE"
    cd "$EVIDENCE" || true
    return "$RC"
  fi

  rm -rf "$VENV"
  printf 'PASS - canonical source and deterministic package validated without changing tracked evidence\n'
  printf 'PASS - evidence preserved at %s\n' "$EVIDENCE"
  cd "$EVIDENCE" || true
}
bn7_m2m_validate_canonical_source
