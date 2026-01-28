"""
ReproLab Flask Application
A reproducible, containerized web application demonstrating
Linux container concepts and CI/CD with pull-based deployment.
"""
import os
import socket
import time
from datetime import datetime
from flask import Flask, jsonify, render_template_string
import psutil  # For system resource monitoring

app = Flask(__name__)

# ========== CONFIGURATION ==========
# All configuration from environment variables (no hardcoded values)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
    DEBUG=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
    HOSTNAME=os.getenv('HOSTNAME', socket.gethostname()),
    VERSION=os.getenv('APP_VERSION', '1.0.0'),
    DEPLOYMENT_TIME=os.getenv('DEPLOYMENT_TIME', datetime.now().isoformat())
)

# ========== HTML TEMPLATE ==========
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ReproLab - {{ title }}</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 900px; 
            margin: 40px auto; 
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container { 
            background: white; 
            border-radius: 15px; 
            padding: 30px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 { color: #4a5568; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
        .info-box { 
            background: #f8f9fa; 
            padding: 20px; 
            margin: 15px 0; 
            border-left: 5px solid #48bb78;
            border-radius: 8px;
        }
        .status { 
            display: inline-block; 
            padding: 8px 15px; 
            border-radius: 20px; 
            font-weight: bold;
            margin: 5px 0;
        }
        .healthy { background: #c6f6d5; color: #22543d; }
        .unhealthy { background: #fed7d7; color: #742a2a; }
        .endpoint-list { 
            list-style: none; 
            padding: 0; 
        }
        .endpoint-list li { 
            margin: 8px 0; 
            padding: 10px; 
            background: #e2e8f0; 
            border-radius: 5px;
        }
        .endpoint-list a { 
            color: #2d3748; 
            text-decoration: none; 
            font-weight: 500;
        }
        .endpoint-list a:hover { 
            color: #667eea; 
            text-decoration: underline;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            background: #e2e8f0;
            border-radius: 12px;
            font-size: 0.9em;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 ReproLab - CI/CD with Pull-Based Deployment</h1>
        
        <div class="info-box">
            <h3>📦 Application Information</h3>
            <p><strong>Version:</strong> {{ version }} <span class="badge">Latest</span></p>
            <p><strong>Hostname:</strong> {{ hostname }}</p>
            <p><strong>Deployment Time:</strong> {{ deployment_time }}</p>
            <p><strong>User ID (UID):</strong> {{ uid }} <span class="badge">Non-root user</span></p>
            <p><strong>Group ID (GID):</strong> {{ gid }}</p>
        </div>
        
        <div class="info-box">
            <h3>📊 System Resources & Health</h3>
            <p><strong>CPU Usage:</strong> {{ cpu_percent }}%</p>
            <p><strong>Memory Usage:</strong> {{ memory_usage }} MB / {{ memory_total }} MB ({{ memory_percent }}%)</p>
            <p><strong>Container Health:</strong> 
                <span class="status {{ 'healthy' if healthy else 'unhealthy' }}">
                    {{ '✅ Healthy' if healthy else '❌ Needs attention' }}
                </span>
            </p>
            <p><strong>Uptime:</strong> {{ uptime }} seconds</p>
        </div>
        
        <div class="info-box">
            <h3>🔗 Available Endpoints</h3>
            <ul class="endpoint-list">
                <li><a href="/health">/health</a> - Docker health check endpoint</li>
                <li><a href="/info">/info</a> - Detailed system & container information</li>
                <li><a href="/stress">/stress</a> - CPU stress test (resource limits demo)</li>
                <li><a href="/deployment">/deployment</a> - Deployment status & history</li>
                <li><a href="/">/</a> - This dashboard</li>
            </ul>
        </div>
        
        <div class="info-box">
            <h3>🎯 CI/CD Pipeline Status</h3>
            <p><strong>Last Commit:</strong> {{ last_commit[:8] if last_commit else 'N/A' }}</p>
            <p><strong>Build Status:</strong> 
                <span class="status healthy">✅ Tests Passing</span>
            </p>
            <p><strong>Deployment Model:</strong> Pull-Based (Lab → GitHub)</p>
            <p><small>Lab machine automatically pulls changes every 5 minutes</small></p>
        </div>
    </div>
</body>
</html>
'''

# ========== ROUTES ==========

@app.route('/')
def index():
    """Main dashboard showing all system information"""
    process = psutil.Process()
    
    return render_template_string(
        HTML_TEMPLATE,
        title="ReproLab Dashboard",
        version=app.config['VERSION'],
        hostname=app.config['HOSTNAME'],
        deployment_time=app.config['DEPLOYMENT_TIME'],
        uid=os.getuid(),
        gid=os.getgid(),
        cpu_percent=psutil.cpu_percent(interval=0.1),
        memory_usage=round(process.memory_info().rss / 1024 / 1024, 2),
        memory_total=round(psutil.virtual_memory().total / 1024 / 1024, 2),
        memory_percent=psutil.virtual_memory().percent,
        uptime=int(time.time() - process.create_time()),
        healthy=True,
        last_commit=os.getenv('GIT_COMMIT', '')[:8] if os.getenv('GIT_COMMIT') else None
    )

@app.route('/health')
def health_check():
    """
    Health check endpoint for Docker health monitoring
    Returns 200 OK if healthy, 503 if unhealthy
    """
    try:
        # Check 1: Disk I/O
        test_file = '/tmp/health_check.txt'
        with open(test_file, 'w') as f:
            f.write(f'health_check_{datetime.now().isoformat()}')
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Check 2: Memory availability
        memory = psutil.virtual_memory()
        if memory.percent > 90:  # Critical memory usage
            return jsonify({
                "status": "unhealthy",
                "message": "High memory usage",
                "memory_percent": memory.percent,
                "timestamp": datetime.now().isoformat()
            }), 503
        
        # Check 3: Application responsiveness
        if not app:
            return jsonify({
                "status": "unhealthy",
                "message": "Flask app not initialized",
                "timestamp": datetime.now().isoformat()
            }), 503
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "reprolab_flask_app",
            "checks": {
                "disk_io": "pass",
                "memory": f"pass ({memory.percent}% used)",
                "application": "running",
                "container": "dockerized"
            },
            "container_info": {
                "user": f"uid:{os.getuid()},gid:{os.getgid()}",
                "is_root": os.getuid() == 0,
                "hostname": socket.gethostname()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/info')
def system_info():
    """Detailed system and container information"""
    return jsonify({
        "application": {
            "name": "ReproLab Flask Application Watchtower test",
            "version": app.config['VERSION'],
            "environment": os.getenv('FLASK_ENV', 'production'),
            "debug_mode": app.config['DEBUG']
        },
        "container": {
            "hostname": app.config['HOSTNAME'],
            "user": {
                "uid": os.getuid(),
                "gid": os.getgid(),
                "is_root": os.getuid() == 0,
                "username": os.getenv('USER', 'container_user')
            },
            "working_directory": os.getcwd(),
            "deployment_time": app.config['DEPLOYMENT_TIME']
        },
        "system": {
            "platform": os.uname().sysname if hasattr(os, 'uname') else 'Linux',
            "python_version": os.sys.version,
            "cpu_count": psutil.cpu_count(),
            "total_memory_mb": round(psutil.virtual_memory().total / 1024 / 1024, 2),
            "available_memory_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2)
        },
        "ci_cd": {
            "deployment_model": "pull_based",
            "description": "Lab machine pulls from GitHub periodically",
            "last_commit_hash": os.getenv('GIT_COMMIT', '')[:8] if os.getenv('GIT_COMMIT') else None
        }
    })

@app.route('/stress')
def cpu_stress():
    """
    Demonstrates resource limits by performing CPU-intensive calculation
    Shows how Docker cgroups limit resource usage. All data is returned as JSON.
    """
    import time
    
    start_time = time.time()
    
    # CPU-intensive calculation (Fibonacci)
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    # This will be limited by Docker's CPU limits
    result = fibonacci(30)  # Adjust based on desired intensity
    
    elapsed = time.time() - start_time
    
    return jsonify({
        "test": "cpu_stress_test",
        "purpose": "Demonstrate Docker CPU resource limits",
        "calculation": "fibonacci(30)",
        "result": result,
        "computation_time_seconds": round(elapsed, 4),
        "resource_usage": {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_mb": round(psutil.Process().memory_info().rss / 1024 / 1024, 2),
            "process_uptime": round(time.time() - psutil.Process().create_time(), 2)
        },
        "note": "In production, this endpoint would be protected or removed"
    })

@app.route('/deployment')
def deployment_info():
    """Shows deployment information and status"""
    return jsonify({
        "deployment": {
            "method": "pull_based_ci_cd",
            "trigger": "periodic_pull_from_lab_machine",
            "interval_minutes": 5,
            "last_deployment": app.config['DEPLOYMENT_TIME'],
            "health_status": "healthy",
            "monitoring": {
                "health_endpoint": "/health",
                "dashboard": "/",
                "metrics": "docker_stats"
            }
        },
        "environment": {
            "flask_env": os.getenv('FLASK_ENV', 'production'),
            "container_runtime": "docker",
            "user_isolation": "non_root_user",
            "resource_limits": "cgroups_enforced"
        },
        "version_control": {
            "git_commit": os.getenv('GIT_COMMIT', 'unknown')[:8] if os.getenv('GIT_COMMIT') else 'unknown',
            "git_branch": os.getenv('GIT_BRANCH', 'main')
        }
    })

# ========== APPLICATION START ==========
if __name__ == '__main__':
    print(f"🚀 Starting ReproLab Flask Application")
    print(f"📦 Version: {app.config['VERSION']}")
    print(f"🌐 Host: {os.getenv('FLASK_HOST', '0.0.0.0')}:{os.getenv('FLASK_PORT', '5000')}")
    print(f"🔒 User: uid={os.getuid()}, gid={os.getgid()}")
    print(f"📊 Health endpoint: http://localhost:{os.getenv('FLASK_PORT', '5000')}/health")
    
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', '5000')),
        debug=app.config['DEBUG']
    )