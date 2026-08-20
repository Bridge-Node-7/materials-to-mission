#!/usr/bin/env bash
set -Eeuo pipefail

echo "BN7 Repository Receipt"
echo

echo "Repository:"
basename "$(git rev-parse --show-toplevel)"

echo
echo "Commit:"
git rev-parse HEAD

echo
echo "Branch:"
git branch --show-current

echo
echo "Status:"
git status --short
