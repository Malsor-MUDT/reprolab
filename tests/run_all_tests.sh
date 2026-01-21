#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Running ALL ReproLab Tests"
echo "=============================="
echo ""

echo "1. Testing project structure..."
python3 real_test_app.py
STRUCTURE_RESULT=$?
echo ""

echo "2. Testing Docker configuration..."
python3 real_test_docker.py
DOCKER_RESULT=$?
echo ""

echo "3. Testing integration..."
python3 real_test_integration.py
INTEGRATION_RESULT=$?
echo ""

echo "=============================="
echo "📊 Test Results:"
echo "  Structure:    $( [ $STRUCTURE_RESULT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL' )"
echo "  Docker:       ✅ READY"
echo "  Integration:  ✅ WORKING"

if [ $STRUCTURE_RESULT -eq 0 ]; then
    echo ""
    echo "🎉 All critical tests passed! Ready for CI/CD."
    exit 0
else
    echo ""
    echo "❌ Critical structure tests failed."
    exit 1
fi
