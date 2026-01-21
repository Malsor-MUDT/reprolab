"""
Unit tests for ReproLab Flask application
"""
import pytest
import json
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Create test client
    with app.test_client() as client:
        # Establish application context
        with app.app_context():
            yield client

def test_health_endpoint_returns_200(client):
    """Test that health endpoint returns 200 OK when healthy"""
    response = client.get('/health')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'checks' in data

def test_health_endpoint_structure(client):
    """Test health endpoint returns correct JSON structure"""
    response = client.get('/health')
    data = json.loads(response.data)
    
    # Check required fields
    required_fields = ['status', 'timestamp', 'service', 'checks']
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    
    # Check nested structure
    assert isinstance(data['checks'], dict)
    assert 'disk_io' in data['checks']
    assert 'memory' in data['checks']
    assert 'application' in data['checks']

def test_info_endpoint_returns_container_info(client):
    """Test system info endpoint returns container information"""
    response = client.get('/info')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    
    # Check top-level sections
    assert 'application' in data
    assert 'container' in data
    assert 'system' in data
    assert 'ci_cd' in data
    
    # Verify non-root user (security demonstration)
    assert data['container']['user']['is_root'] == False
    
    # Verify deployment model
    assert data['ci_cd']['deployment_model'] == 'pull_based'

def test_main_page_loads(client):
    """Test that main application page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    # Check for key content in HTML
    assert b'ReproLab' in response.data
    assert b'Dashboard' in response.data
    assert b'CI/CD' in response.data

def test_stress_endpoint_returns_json(client):
    """Test CPU stress endpoint returns valid JSON"""
    response = client.get('/stress')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'test' in data
    assert 'purpose' in data
    assert 'calculation' in data
    assert 'resource_usage' in data
    assert data['test'] == 'cpu_stress_test'

def test_deployment_endpoint(client):
    """Test deployment info endpoint"""
    response = client.get('/deployment')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'deployment' in data
    assert 'environment' in data
    assert 'version_control' in data
    
    # Verify deployment method
    assert data['deployment']['method'] == 'pull_based_ci_cd'

def test_environment_variables_configuration():
    """Test that app configuration uses environment variables"""
    import os
    
    # Test with different environment variable
    os.environ['FLASK_ENV'] = 'testing'
    
    # Re-import to pick up new env var
    import importlib
    import sys
    if 'app' in sys.modules:
        importlib.reload(sys.modules['app'])
    
    from app import app as reloaded_app
    assert reloaded_app.config['DEBUG'] == False  # Should be False in production mode

def test_error_handling(client):
    """Test that non-existent endpoints return 404"""
    response = client.get('/nonexistent')
    assert response.status_code == 404

def test_cors_headers(client):
    """Test that CORS headers are present (if needed)"""
    response = client.get('/health')
    # Flask doesn't add CORS by default, but we can check other headers
    assert 'Content-Type' in response.headers
    assert response.headers['Content-Type'] == 'application/json'
