#!/bin/bash
# Script to publish rm530-5g-integration to PyPI

echo "🚀 Publishing rm530-5g-integration v3.0.0 to PyPI"
echo ""

# Check if credentials are set
if [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
    echo "⚠️  TWINE_USERNAME and TWINE_PASSWORD environment variables not set"
    echo ""
    echo "Option 1: Set environment variables:"
    echo "  export TWINE_USERNAME=__token__"
    echo "  export TWINE_PASSWORD=pypi-your-api-token"
    echo "  ./publish.sh"
    echo ""
    echo "Option 2: Use interactive mode (will prompt for credentials):"
    echo "  python3 -m twine upload dist/*"
    echo ""
    echo "Option 3: Test PyPI first (recommended):"
    echo "  python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
    exit 1
fi

echo "✅ Credentials found in environment"
echo ""

# Upload to PyPI
echo "Uploading to PyPI..."
python3 -m twine upload dist/*

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully published to PyPI!"
    echo ""
    echo "Package URL: https://pypi.org/project/rm530-5g-integration/3.0.0/"
    echo ""
    echo "Test installation:"
    echo "  pip install rm530-5g-integration==3.0.0"
else
    echo ""
    echo "❌ Upload failed. Check error messages above."
    exit 1
fi

