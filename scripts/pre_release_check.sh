#!/bin/bash
# Just a dev script to help me check some things before release.
# John R. April 2025

echo "Check versions set correctly"
perl -e 'print "-" x 40; print "\n"' # <3 perl!
echo -n "Git Branch: "
git branch --show-current
grep -H "version" tests/test_vars.json
grep -HoP 'Version: \d\.\d\.\d' app/templates/base.html

echo "Downloading latest coverage badge using gh cli..."
set -x
cd docs/images/
rm coverage-badge.svg
gh run download --name coverage-badge-3.12
cd -
set +x
echo "Coverage Badge Updated!"
