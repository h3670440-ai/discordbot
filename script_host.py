"""
Script hosting endpoint with password protection
Serves Lua scripts with beautiful web interface
"""
from flask import render_template_string, request, jsonify, send_from_directory
import os
import hashlib

# Password for accessing scripts
SCRIPT_PASSWORD = "vanitymogsulol"

# HTML template with beautiful design and animations
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vanity Script Hub</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            position: relative;
        }

        /* Animated background particles */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 0;
        }

        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 50%;
            animation: float 15s infinite;
        }

        @keyframes float {
            0%, 100% {
                transform: translateY(0) translateX(0);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100vh) translateX(100px);
                opacity: 0;
            }
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            padding: 50px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 90%;
            text-align: center;
            position: relative;
            z-index: 1;
            animation: slideIn 0.5s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .logo {
            font-size: 48px;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            animation: glow 2s ease-in-out infinite;
        }

        @keyframes glow {
            0%, 100% {
                filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5));
            }
            50% {
                filter: drop-shadow(0 0 20px rgba(118, 75, 162, 0.8));
            }
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }

        .input-group {
            margin-bottom: 20px;
            position: relative;
        }

        input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            outline: none;
        }

        input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }

        button:active {
            transform: translateY(0);
        }

        button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        button:active::before {
            width: 300px;
            height: 300px;
        }

        .error {
            color: #e74c3c;
            margin-top: 15px;
            font-size: 14px;
            animation: shake 0.5s;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }

        .success {
            color: #27ae60;
            margin-top: 15px;
            font-size: 14px;
            animation: fadeIn 0.5s;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .script-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            text-align: left;
        }

        .script-info h3 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .code-block {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
            margin-top: 10px;
            position: relative;
        }

        .copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #667eea;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s ease;
        }

        .copy-btn:hover {
            background: #764ba2;
        }

        .footer {
            margin-top: 30px;
            color: #999;
            font-size: 12px;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="particles" id="particles"></div>
    
    <div class="container">
        <div class="logo">VANITY</div>
        <div class="subtitle">Premium Script Hub</div>
        
        <div id="loginForm">
            <div class="input-group">
                <input type="password" id="password" placeholder="Enter Access Code" autocomplete="off">
            </div>
            <button onclick="authenticate()">
                <span id="btnText">ACCESS SCRIPT</span>
            </button>
            <div id="message"></div>
        </div>

        <div id="scriptContent" style="display: none;">
            <div class="script-info">
                <h3>🎯 Vanity Script</h3>
                <p><strong>Status:</strong> <span style="color: #27ae60;">✓ Active</span></p>
                <p><strong>Version:</strong> Latest</p>
                <p><strong>Last Updated:</strong> {{ timestamp }}</p>
                
                <div style="margin-top: 20px;">
                    <strong>Loadstring:</strong>
                    <div class="code-block">
                        <button class="copy-btn" onclick="copyLoadstring()">Copy</button>
                        <code id="loadstring">loadstring(game:HttpGet("{{ script_url }}"))();</code>
                    </div>
                </div>

                <div style="margin-top: 15px;">
                    <strong>Direct Script URL:</strong>
                    <div class="code-block">
                        <button class="copy-btn" onclick="copyUrl()">Copy</button>
                        <code id="scriptUrl">{{ script_url }}</code>
                    </div>
                </div>
            </div>

            <button onclick="logout()" style="margin-top: 20px; background: #e74c3c;">
                LOGOUT
            </button>
        </div>

        <div class="footer">
            Vanity © 2026 | Premium Security
        </div>
    </div>

    <script>
        // Create animated particles
        const particlesContainer = document.getElementById('particles');
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 15 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
            particlesContainer.appendChild(particle);
        }

        function authenticate() {
            const password = document.getElementById('password').value;
            const btnText = document.getElementById('btnText');
            const message = document.getElementById('message');
            
            btnText.innerHTML = '<span class="loading"></span>';
            
            fetch('/api/authenticate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ password: password })
            })
            .then(response => response.json())
            .then(data => {
                btnText.textContent = 'ACCESS SCRIPT';
                if (data.success) {
                    message.innerHTML = '<div class="success">✓ Access Granted</div>';
                    setTimeout(() => {
                        document.getElementById('loginForm').style.display = 'none';
                        document.getElementById('scriptContent').style.display = 'block';
                    }, 500);
                } else {
                    message.innerHTML = '<div class="error">✗ Invalid Access Code</div>';
                    document.getElementById('password').value = '';
                }
            })
            .catch(error => {
                btnText.textContent = 'ACCESS SCRIPT';
                message.innerHTML = '<div class="error">✗ Connection Error</div>';
            });
        }

        function copyLoadstring() {
            const text = document.getElementById('loadstring').textContent;
            navigator.clipboard.writeText(text);
            alert('Loadstring copied to clipboard!');
        }

        function copyUrl() {
            const text = document.getElementById('scriptUrl').textContent;
            navigator.clipboard.writeText(text);
            alert('URL copied to clipboard!');
        }

        function logout() {
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('scriptContent').style.display = 'none';
            document.getElementById('password').value = '';
            document.getElementById('message').innerHTML = '';
        }

        // Allow Enter key to submit
        document.getElementById('password').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                authenticate();
            }
        });
    </script>
</body>
</html>
"""

def add_script_hosting_routes(app):
    """Add script hosting routes to the Flask app"""
    
    @app.route('/script')
    def script_page():
        """Serve the password-protected script page"""
        import datetime
        script_url = request.host_url + 'api/script/raw'
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render_template_string(HTML_TEMPLATE, script_url=script_url, timestamp=timestamp)
    
    @app.route('/api/authenticate', methods=['POST'])
    def authenticate():
        """Authenticate password"""
        data = request.get_json()
        password = data.get('password', '')
        
        if password == SCRIPT_PASSWORD:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    
    @app.route('/api/script/raw')
    def get_raw_script():
        """Serve the raw Lua script"""
        # Check if script file exists
        script_path = 'vanitynew.lua'
        if os.path.exists(script_path):
            with open(script_path, 'r') as f:
                script_content = f.read()
            return script_content, 200, {'Content-Type': 'text/plain'}
        else:
            return "-- Script not found. Please upload vanitynew.lua", 404, {'Content-Type': 'text/plain'}
