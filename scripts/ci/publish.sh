#!/usr/bin/env bash
# Publish through the existing Make target and report the result to Actions.
set -euo pipefail

PYTHON=${PYTHON:-python}
if [ -z "${GITHUB_STEP_SUMMARY:-}" ]; then
    GITHUB_STEP_SUMMARY=$(mktemp)
    trap 'cat "$GITHUB_STEP_SUMMARY"; rm -f "$GITHUB_STEP_SUMMARY"' EXIT
fi

echo "## 📦 Publishing to PyPI" >> "$GITHUB_STEP_SUMMARY"
if make publish > publish_output.txt 2>&1; then
  # Extract package name and version
  PACKAGE_NAME=$("$PYTHON" -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'])")
  PACKAGE_VERSION=$("$PYTHON" -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")

  echo "✅ **Package published successfully!**" >> "$GITHUB_STEP_SUMMARY"
  echo "" >> "$GITHUB_STEP_SUMMARY"
  echo "### 📋 Package Details:" >> "$GITHUB_STEP_SUMMARY"
  echo "- **Package:** \`$PACKAGE_NAME\`" >> "$GITHUB_STEP_SUMMARY"
  echo "- **Version:** \`$PACKAGE_VERSION\`" >> "$GITHUB_STEP_SUMMARY"
  echo "- **Repository:** PyPI" >> "$GITHUB_STEP_SUMMARY"
  echo "" >> "$GITHUB_STEP_SUMMARY"
  echo "### 🔗 Links:" >> "$GITHUB_STEP_SUMMARY"
  echo "- [View on PyPI](https://pypi.org/project/$PACKAGE_NAME/$PACKAGE_VERSION/)" >> "$GITHUB_STEP_SUMMARY"
  echo "- [Install command](https://pypi.org/project/$PACKAGE_NAME/#description): \`pip install $PACKAGE_NAME==$PACKAGE_VERSION\`" >> "$GITHUB_STEP_SUMMARY"
else
  echo "❌ **Publishing failed!**" >> "$GITHUB_STEP_SUMMARY"
  echo "" >> "$GITHUB_STEP_SUMMARY"
  echo "### Error details:" >> "$GITHUB_STEP_SUMMARY"
  echo '```' >> "$GITHUB_STEP_SUMMARY"
  cat publish_output.txt >> "$GITHUB_STEP_SUMMARY"
  echo '```' >> "$GITHUB_STEP_SUMMARY"
  echo "" >> "$GITHUB_STEP_SUMMARY"
  echo "💡 **Common fixes:**" >> "$GITHUB_STEP_SUMMARY"
  echo "- Check if version already exists on PyPI" >> "$GITHUB_STEP_SUMMARY"
  echo "- Verify \`PYPI_API_TOKEN\` secret is set correctly" >> "$GITHUB_STEP_SUMMARY"
  echo "- Ensure package name is available" >> "$GITHUB_STEP_SUMMARY"
  exit 1
fi
