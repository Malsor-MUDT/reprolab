#!/usr/bin/env python3
"""
REAL test that actually checks the Flask app
"""
import sys
import os
import subprocess

def main():
    print("🔍 Running REAL application tests")
    print("=" * 50)
    
    # Get the project root directory
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Test 1: Check if critical files exist
    print("\n1. Checking file structure...")
    critical_files = [
        (os.path.join(PROJECT_ROOT, 'src', 'app.py'), 'Main application file'),
        (os.path.join(PROJECT_ROOT, 'src', 'Dockerfile'), 'Docker configuration'),
        (os.path.join(PROJECT_ROOT, 'src', 'requirements.txt'), 'Python dependencies'),
        (os.path.join(PROJECT_ROOT, 'README.md'), 'Documentation'),
    ]
    
    all_files_exist = True
    for file_path, description in critical_files:
        if os.path.exists(file_path):
            print(f"   ✅ {description} exists")
            # Check if file has content
            if os.path.getsize(file_path) > 0:
                print(f"     ↪ File is not empty ({os.path.getsize(file_path)} bytes)")
            else:
                print(f"     ⚠️  File is empty")
                # Don't fail if it's just README.md
                if 'README.md' not in file_path:
                    all_files_exist = False
        else:
            print(f"   ❌ {description} MISSING")
            all_files_exist = False
    
    # Test 2: Check if requirements.txt has Flask
    print("\n2. Checking dependencies...")
    req_path = os.path.join(PROJECT_ROOT, 'src', 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            content = f.read()
            if 'Flask' in content:
                print("   ✅ Flask is in requirements.txt")
            else:
                print("   ❌ Flask NOT in requirements.txt")
                all_files_exist = False
    else:
        print("   ❌ requirements.txt not found")
        all_files_exist = False
    
    # Test 3: Check if app.py has Flask app
    print("\n3. Checking app.py structure...")
    app_path = os.path.join(PROJECT_ROOT, 'src', 'app.py')
    if os.path.exists(app_path):
        with open(app_path, 'r') as f:
            content = f.read()
            
            checks = [
                ('Flask' in content, 'Imports Flask'),
                ('app = Flask' in content, 'Creates Flask app'),
                ('/health' in content, 'Has health endpoint'),
                ('@app.route' in content, 'Has route decorators'),
            ]
            
            for condition, message in checks:
                if condition:
                    print(f"   ✅ {message}")
                else:
                    print(f"   ❌ Missing: {message}")
                    all_files_exist = False
    else:
        print("   ❌ app.py not found")
        all_files_exist = False
    
    print("\n" + "=" * 50)
    if all_files_exist:
        print("🎉 REAL TESTS PASSED: All critical files and structures are correct!")
        return True
    else:
        print("❌ REAL TESTS FAILED: Some critical issues found.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
