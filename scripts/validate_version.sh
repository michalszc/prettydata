#!/usr/bin/env bash
# Validate version consistency across project files, release notes, and PyPI.
set -euo pipefail

PYTHON=${PYTHON:-python}
offline=false
case "${1:-}" in
    "") ;;
    --offline) offline=true; shift ;;
    *) echo "usage: $0 [--offline]" >&2; exit 2 ;;
esac
if [ "$#" -ne 0 ]; then
    echo "usage: $0 [--offline]" >&2
    exit 2
fi

echo "🔍 Validating version consistency..."
PYPROJECT_VERSION=$("$PYTHON" -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
INIT_VERSION=$("$PYTHON" -c "import sys; sys.path.insert(0, 'src'); import prettydata; print(prettydata.__version__)")
echo "📄 pyproject.toml: $PYPROJECT_VERSION"
echo "📄 __init__.py:    $INIT_VERSION"
if [ "$PYPROJECT_VERSION" != "$INIT_VERSION" ]; then
    echo "❌ Version mismatch between pyproject.toml and __init__.py!" >&2
    exit 1
fi

"$PYTHON" - "$PYPROJECT_VERSION" <<'PY'
import re
import sys
from pathlib import Path

version = sys.argv[1]
path = Path('documentation/release-notes.md')
if not path.is_file():
    sys.exit(f'Release notes file not found: {path}')
lines = path.read_text(encoding='utf-8').splitlines()
matches = [i for i, line in enumerate(lines) if re.match(r'^##\s+' + re.escape(version) + r'(?:\s|$)', line)]
if not matches:
    sys.exit(f'Version {version} is missing from {path}')
if len(matches) != 1:
    sys.exit(f'Version {version} appears multiple times in {path}')
start = matches[0] + 1
end = next((i for i in range(start, len(lines)) if re.match(r'^##\s+', lines[i])), len(lines))
if not '\n'.join(lines[start:end]).strip():
    sys.exit(f'Empty release-notes section for {version}')
print('✅ Current version is included exactly once in release notes with nonempty notes')
PY

if [ "$offline" = true ]; then
    echo "ℹ️  Offline validation: PyPI comparison skipped"
    exit 0
fi

PACKAGE_NAME=$("$PYTHON" -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'])")
response=$(mktemp)
trap 'rm -f "$response"' EXIT
if ! status=$(curl --silent --show-error --location --connect-timeout 10 --max-time 30 \
    --output "$response" --write-out '%{http_code}' "https://pypi.org/pypi/${PACKAGE_NAME}/json"); then
    echo "❌ Could not contact PyPI; use --offline for local-only validation" >&2
    exit 1
fi
case "$status" in
    404) echo "ℹ️  Package '${PACKAGE_NAME}' not found on PyPI (first release?)" ;;
    200)
        PYPI_VERSION=$("$PYTHON" -c 'import json, sys; print(json.load(open(sys.argv[1]))["info"]["version"])' "$response")
        echo "📦 PyPI: $PYPI_VERSION"
        if [ "$PYPROJECT_VERSION" = "$PYPI_VERSION" ]; then
            echo "❌ Version matches PyPI! Please bump the version before publishing." >&2
            exit 1
        fi
        ;;
    *) echo "❌ PyPI returned HTTP $status" >&2; exit 1 ;;
esac
echo "✅ All checks passed for version $PYPROJECT_VERSION"
