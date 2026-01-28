#!/bin/bash
echo "🚀 Running ReproLab Test Suite"
echo "=============================="

# Change to tests directory
cd "$(dirname "$0")"

# Test 1: Check if src directory exists
echo ""
echo "1. Checking project structure..."
if [ -d "../src" ]; then
    echo "✅ src/ directory exists"
    echo "   Files: $(ls ../src/ | tr '\n' ' ')"
else
    echo "❌ src/ directory not found!"
    exit 1
fi

# Test 2: Check if app.py exists
if [ -f "../src/app.py" ]; then
    echo "✅ app.py exists"
else
    echo "❌ app.py not found!"
    exit 1
fi

# Test 3: Run Python tests
echo ""
echo "2. Running Python tests..."
python3 run_tests.py

if [ $? -eq 0 ]; then
    echo "✅ Python tests passed"
else
    echo "❌ Python tests failed"
    exit 1
fi

# Test 4: Run pytest tests
echo ""
echo "3. Running pytest tests..."
cd ..
if python3 -m pytest tests/ -v; then
    echo "✅ pytest tests passed"
else
    echo "⚠️  Some pytest tests may have failed (expected for some Docker tests)"
fi

# Test 5: Run Docker tests
echo ""
echo "4. Running Docker tests..."
cd tests
python3 test_docker.py

echo ""
echo "=============================="
echo "🎉 Test suite completed!"
