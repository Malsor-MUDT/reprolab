"""
Tests for Docker configuration and container behavior
These tests simulate what will happen in CI pipeline
"""
import os
import subprocess
import time
import requests

def test_dockerfile_exists():
    """Test that Dockerfile exists and is readable"""
    assert os.path.exists('src/Dockerfile'), "Dockerfile not found"
    with open('src/Dockerfile', 'r') as f:
        content = f.read()
        assert 'FROM python' in content, "Dockerfile should start with Python"
        assert 'USER appuser' in content, "Dockerfile should use non-root user"

def test_docker_compose_exists():
    """Test that docker-compose.yml exists"""
    assert os.path.exists('src/docker-compose.yml'), "docker-compose.yml not found"

def test_requirements_file():
    """Test that requirements.txt exists and has expected packages"""
    assert os.path.exists('src/requirements.txt'), "requirements.txt not found"
    with open('src/requirements.txt', 'r') as f:
        content = f.read()
        assert 'Flask' in content
        assert 'psutil' in content

def test_docker_build():
    """
    Test that Docker image can be built
    This simulates what GitHub Actions will do
    """
    try:
        # Change to src directory
        original_dir = os.getcwd()
        os.chdir('src')
        
        # Build Docker image (this is what CI will do)
        result = subprocess.run(
            ['docker', 'build', '-t', 'reprolab-test', '.'],
            capture_output=True,
            text=True
        )
        
        # Check if build was successful
        assert result.returncode == 0, f"Docker build failed: {result.stderr}"
        
        # Check that image was created
        result = subprocess.run(
            ['docker', 'images', 'reprolab-test'],
            capture_output=True,
            text=True
        )
        assert 'reprolab-test' in result.stdout
        
        # Clean up test image
        subprocess.run(['docker', 'rmi', 'reprolab-test'], capture_output=True)
        
    finally:
        os.chdir(original_dir)

def test_container_health_check():
    """
    Test that container health check works
    This simulates Docker's health check mechanism
    """
    try:
        original_dir = os.getcwd()
        os.chdir('src')
        
        # Build and run test container
        build_result = subprocess.run(
            ['docker', 'build', '-t', 'reprolab-health-test', '.'],
            capture_output=True,
            text=True
        )
        assert build_result.returncode == 0
        
        # Run container in background
        run_result = subprocess.run([
            'docker', 'run', '-d',
            '--name', 'reprolab-health-container',
            '-p', '5002:5000',
            'reprolab-health-test'
        ], capture_output=True, text=True)
        assert run_result.returncode == 0
        
        # Wait for container to start
        time.sleep(10)
        
        # Test health endpoint manually
        response = requests.get('http://localhost:5002/health', timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        
        # Check Docker health status
        health_result = subprocess.run([
            'docker', 'inspect',
            '--format', '{{.State.Health.Status}}',
            'reprolab-health-container'
        ], capture_output=True, text=True)
        
        if health_result.returncode == 0:
            # Health check might still be running
            assert health_result.stdout.strip() in ['healthy', 'starting']
        
        # Clean up
        subprocess.run(['docker', 'stop', 'reprolab-health-container'], capture_output=True)
        subprocess.run(['docker', 'rm', 'reprolab-health-container'], capture_output=True)
        subprocess.run(['docker', 'rmi', 'reprolab-health-test'], capture_output=True)
        
    except requests.RequestException as e:
        print(f"Health check request failed: {e}")
        # Clean up on failure
        subprocess.run(['docker', 'stop', 'reprolab-health-container'], capture_output=True, stderr=subprocess.DEVNULL)
        subprocess.run(['docker', 'rm', 'reprolab-health-container'], capture_output=True, stderr=subprocess.DEVNULL)
        subprocess.run(['docker', 'rmi', 'reprolab-health-test'], capture_output=True, stderr=subprocess.DEVNULL)
        raise
    finally:
        os.chdir(original_dir)

def test_non_root_user():
    """Test that container runs as non-root user"""
    try:
        original_dir = os.getcwd()
        os.chdir('src')
        
        # Run container and check user
        run_result = subprocess.run([
            'docker', 'run', '--rm',
            'reprolab-health-test',
            'sh', '-c', 'whoami && id -u'
        ], capture_output=True, text=True, timeout=10)
        
        assert run_result.returncode == 0
        output = run_result.stdout.strip().split('\n')
        
        # Should run as appuser, not root
        assert 'appuser' in output[0] or '1000' in output[1]
        
    finally:
        os.chdir(original_dir)

if __name__ == '__main__':
    # Run tests directly
    test_dockerfile_exists()
    test_docker_compose_exists()
    test_requirements_file()
    print("✅ All Docker configuration tests passed!")
