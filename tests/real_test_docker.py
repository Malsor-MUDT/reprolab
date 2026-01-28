#!/usr/bin/env python3
"""
REAL Docker tests - WITH CORRECT PATHS
"""
import os
import subprocess

print("🔧 Running REAL Docker infrastructure tests")
print("=" * 50)

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

print(f"Project root: {PROJECT_ROOT}")
print(f"Source dir: {SRC_DIR}")

# Test 1: Check Docker is available
print("\n1. Checking Docker availability...")
try:
    result = subprocess.run(
        ['docker', '--version'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"   ✅ Docker is installed: {result.stdout.strip()}")
    else:
        print(f"   ❌ Docker not working: {result.stderr}")
        docker_available = False
except FileNotFoundError:
    print("   ❌ Docker command not found (Docker not installed)")
    docker_available = False
except Exception as e:
    print(f"   ❌ Docker check failed: {e}")
    docker_available = False
else:
    docker_available = True

# Test 2: Check Dockerfile
dockerfile_path = os.path.join(SRC_DIR, 'Dockerfile')
print(f"\n2. Checking Dockerfile at: {dockerfile_path}")
if os.path.exists(dockerfile_path):
    with open(dockerfile_path, 'r') as f:
        lines = f.readlines()
        
        checks = [
            (any('FROM ' in line.upper() for line in lines), 'Has FROM instruction'),
            (any('WORKDIR ' in line.upper() for line in lines), 'Has WORKDIR instruction'),
            (any('COPY ' in line.upper() for line in lines), 'Has COPY instruction'),
            (any('EXPOSE ' in line.upper() for line in lines), 'Has EXPOSE instruction'),
            (any('CMD ' in line.upper() for line in lines) or 
             any('ENTRYPOINT ' in line.upper() for line in lines), 'Has CMD/ENTRYPOINT'),
        ]
        
        for condition, message in checks:
            if condition:
                print(f"   ✅ {message}")
            else:
                print(f"   ⚠️  {message} (warning)")
else:
    print(f"   ❌ Dockerfile not found at: {dockerfile_path}")

# Test 3: Check docker-compose.yml
compose_path = os.path.join(SRC_DIR, 'docker-compose.yml')
print(f"\n3. Checking docker-compose.yml at: {compose_path}")
if os.path.exists(compose_path):
    with open(compose_path, 'r') as f:
        content = f.read()
        
        checks = [
            ('version:' in content, 'Has version'),
            ('services:' in content, 'Has services section'),
            ('build:' in content or 'image:' in content, 'Has build/image config'),
            ('ports:' in content, 'Has port mapping'),
        ]
        
        for condition, message in checks:
            if condition:
                print(f"   ✅ {message}")
            else:
                print(f"   ⚠️  {message} (warning)")
else:
    print(f"   ❌ docker-compose.yml not found at: {compose_path}")

# Test 4: Check .env.example
env_path = os.path.join(SRC_DIR, '.env.example')
print(f"\n4. Checking .env.example at: {env_path}")
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        content = f.read()
        if 'FLASK_' in content or 'SECRET_KEY' in content:
            print("   ✅ .env.example has configuration variables")
        else:
            print("   ⚠️  .env.example may be incomplete")
else:
    print("   ⚠️  .env.example not found (warning)")

print("\n" + "=" * 50)
print("🎉 Docker infrastructure tests completed!")
