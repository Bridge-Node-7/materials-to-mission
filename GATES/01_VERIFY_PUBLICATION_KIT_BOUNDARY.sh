#!/usr/bin/env bash
bn7_m2m_verify_publication_kit_boundary(){
  set -Eeuo pipefail
  local ROOT=''
  printf '%s\n' 'WAIT - VERIFY MATERIALS-TO-MISSION PUBLICATION-KIT BOUNDARY'
  printf '%s\n' 'BOUNDARY - local source and contract verification only; no GitHub read or write, no tag, no release'

  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  (cd "$ROOT" && python3 scripts/check_gate_contracts.py) || return 20

  for forbidden in CANDIDATE_IDENTITY.json '*.gitbundle' release-candidate.env; do
    if find "$ROOT" -maxdepth 1 -name "$forbidden" -print -quit | grep -q .; then
      printf 'STOP - publication-kit artifact is incorrectly present in the public source: %s\n' "$forbidden"
      return 20
    fi
  done

  printf '%s\n' 'PASS - public source contains local maintainer gates only'
  printf '%s\n' 'PASS - exact Git identity and public-write gates belong only to a separately reviewed publication kit'
}
bn7_m2m_verify_publication_kit_boundary
