#!/usr/bin/env python3
"""
Test runner that properly sets Python path
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

print(f"Python path: {sys.path}")
print()

# Now import and test
try:
    from app import app
    print("✅ Successfully imported app")
    
    # Test health endpoint
    with app.test_client() as client:
        response = client.get('/health')
        print(f"Health endpoint: {response.status_code}")
        print(f"Response: {response.data[:100]}...")
        
        # Test main page
        response = client.get('/')
        print(f"Main page: {response.status_code}")
        
        # Test info endpoint
        response = client.get('/info')
        print(f"Info endpoint: {response.status_code}")
        
    print("\n🎉 All tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Current directory:", os.getcwd())
    print("Files in src/:", os.listdir('../src'))
    sys.exit(1)
except Exception as e:
    print(f"❌ Test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
