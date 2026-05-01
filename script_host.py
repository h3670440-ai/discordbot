"""
Script hosting endpoint with password protection
Serves Lua scripts with beautiful web interface
"""
from flask import render_template_string, request, jsonify, redirect
import datetime

# Password for accessing scripts
SCRIPT_PASSWORD = "vanitymogsulol"
# Admin password for uploading scripts
ADMIN_PASSWORD = "vanitymogsulol"
# Discord server invite
DISCORD_INVITE = "https://discord.gg/7fvPqf2W9t"

# Store the script content in memory
SCRIPT_CONTENT = """-- Vanity Script
-- Upload your script using the admin panel
print("Please upload your script at /admin")
"""

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
            background: #0a0a0a;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            position: relative;
        }

        /* Animated background with grid and particles */
        .background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            background: 
                linear-gradient(90deg, rgba(138, 43, 226, 0.03) 1px, transparent 1px),
                linear-gradient(rgba(138, 43, 226, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: gridMove 20s linear infinite;
        }

        @keyframes gridMove {
            0% { background-position: 0 0; }
            100% { background-position: 50px 50px; }
        }

        /* Glowing orbs */
        .orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(60px);
            opacity: 0.4;
            animation: float 20s infinite;
        }

        .orb1 {
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, #8a2be2, transparent);
            top: -200px;
            left: -200px;
            animation-delay: 0s;
        }

        .orb2 {
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, #9370db, transparent);
            bottom: -150px;
            right: -150px;
            animation-delay: 5s;
        }

        .orb3 {
            width: 350px;
            height: 350px;
            background: radial-gradient(circle, #ba55d3, transparent);
            top: 50%;
            left: 50%;
            animation-delay: 10s;
        }

        @keyframes float {
            0%, 100% {
                transform: translate(0, 0) scale(1);
            }
            33% {
                transform: translate(100px, -100px) scale(1.1);
            }
            66% {
                transform: translate(-100px, 100px) scale(0.9);
            }
        }

        /* Particles */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 1;
        }

        .particle {
            position: absolute;
            width: 3px;
            height: 3px;
            background: #8a2be2;
            border-radius: 50%;
            box-shadow: 0 0 10px #8a2be2;
            animation: particleFloat 15s infinite;
        }

        @keyframes particleFloat {
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
            background: rgba(15, 15, 15, 0.95);
            backdrop-filter: blur(20px);
            padding: 50px;
            border-radius: 20px;
            border: 1px solid rgba(138, 43, 226, 0.3);
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.5),
                0 0 100px rgba(138, 43, 226, 0.2),
                inset 0 0 50px rgba(138, 43, 226, 0.05);
            max-width: 500px;
            width: 90%;
            text-align: center;
            position: relative;
            z-index: 2;
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
            font-size: 56px;
            font-weight: bold;
            background: linear-gradient(135deg, #ffffff 0%, #8a2be2 50%, #ffffff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
            animation: glow 3s ease-in-out infinite;
            text-shadow: 0 0 30px rgba(138, 43, 226, 0.5);
            letter-spacing: 5px;
        }

        @keyframes glow {
            0%, 100% {
                filter: drop-shadow(0 0 20px rgba(138, 43, 226, 0.8));
            }
            50% {
                filter: drop-shadow(0 0 40px rgba(138, 43, 226, 1));
            }
        }

        .subtitle {
            color: #9370db;
            margin-bottom: 30px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 3px;
        }

        .input-group {
            margin-bottom: 20px;
            position: relative;
        }

        input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid rgba(138, 43, 226, 0.3);
            background: rgba(20, 20, 20, 0.8);
            color: #ffffff;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            outline: none;
        }

        input:focus {
            border-color: #8a2be2;
            box-shadow: 0 0 20px rgba(138, 43, 226, 0.4);
            background: rgba(25, 25, 25, 0.9);
        }

        input::placeholder {
            color: #666;
        }

        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #8a2be2 0%, #9370db 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(138, 43, 226, 0.6);
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
            color: #ff4757;
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
            color: #2ed573;
            margin-top: 15px;
            font-size: 14px;
            animation: fadeIn 0.5s;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .script-info {
            background: rgba(20, 20, 20, 0.8);
            border: 1px solid rgba(138, 43, 226, 0.3);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            text-align: left;
        }

        .script-info h3 {
            color: #8a2be2;
            margin-bottom: 15px;
            font-size: 20px;
        }

        .script-info p {
            color: #ccc;
            margin-bottom: 10px;
        }

        .code-block {
            background: #1a1a1a;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(138, 43, 226, 0.3);
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
            background: #8a2be2;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s ease;
        }

        .copy-btn:hover {
            background: #9370db;
            box-shadow: 0 0 15px rgba(138, 43, 226, 0.6);
        }

        .footer {
            margin-top: 30px;
            color: #666;
            font-size: 12px;
        }

        .footer a {
            color: #8a2be2;
            text-decoration: none;
            transition: all 0.3s ease;
        }

        .footer a:hover {
            color: #9370db;
            text-shadow: 0 0 10px rgba(138, 43, 226, 0.8);
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

        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            background: rgba(46, 213, 115, 0.2);
            border: 1px solid #2ed573;
            border-radius: 20px;
            color: #2ed573;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>
    <div class="background"></div>
    <div class="orb orb1"></div>
    <div class="orb orb2"></div>
    <div class="orb orb3"></div>
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
                <p><strong>Status:</strong> <span class="status-badge">✓ Active</span></p>
                <p><strong>Version:</strong> Latest</p>
                <p><strong>Last Updated:</strong> {{ timestamp }}</p>
                
                <div style="margin-top: 20px;">
                    <strong style="color: #8a2be2;">Loadstring:</strong>
                    <div class="code-block">
                        <button class="copy-btn" onclick="copyLoadstring()">Copy</button>
                        <code id="loadstring">loadstring(game:HttpGet("{{ script_url }}"))();</code>
                    </div>
                </div>

                <div style="margin-top: 15px;">
                    <strong style="color: #8a2be2;">Direct Script URL:</strong>
                    <div class="code-block">
                        <button class="copy-btn" onclick="copyUrl()">Copy</button>
                        <code id="scriptUrl">{{ script_url }}</code>
                    </div>
                </div>
            </div>

            <button onclick="logout()" style="margin-top: 20px; background: linear-gradient(135deg, #ff4757 0%, #ff6348 100%);">
                LOGOUT
            </button>
        </div>

        <div class="footer">
            Vanity © 2026 | <a href="{{ discord_invite }}" target="_blank">Join Discord</a>
        </div>
    </div>

    <script>
        // Create animated particles
        const particlesContainer = document.getElementById('particles');
        for (let i = 0; i < 80; i++) {
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

# Admin panel HTML
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vanity Admin Panel</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: rgba(15, 15, 15, 0.95);
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }

        h1 {
            color: #8a2be2;
            margin-bottom: 10px;
            font-size: 36px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            color: #8a2be2;
            margin-bottom: 10px;
            font-weight: bold;
        }

        input[type="password"] {
            width: 100%;
            padding: 15px;
            background: rgba(20, 20, 20, 0.8);
            border: 2px solid rgba(138, 43, 226, 0.3);
            border-radius: 10px;
            color: #fff;
            font-size: 16px;
        }

        textarea {
            width: 100%;
            min-height: 400px;
            padding: 15px;
            background: #1a1a1a;
            border: 2px solid rgba(138, 43, 226, 0.3);
            border-radius: 10px;
            color: #f8f8f2;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
        }

        button {
            padding: 15px 40px;
            background: linear-gradient(135deg, #8a2be2 0%, #9370db 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(138, 43, 226, 0.6);
        }

        .message {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            display: none;
        }

        .success {
            background: rgba(46, 213, 115, 0.2);
            border: 1px solid #2ed573;
            color: #2ed573;
        }

        .error {
            background: rgba(255, 71, 87, 0.2);
            border: 1px solid #ff4757;
            color: #ff4757;
        }

        .info {
            background: rgba(138, 43, 226, 0.2);
            border: 1px solid #8a2be2;
            color: #8a2be2;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .info strong {
            display: block;
            margin-bottom: 10px;
        }

        .info code {
            background: #1a1a1a;
            padding: 2px 8px;
            border-radius: 5px;
            color: #9370db;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Vanity Admin Panel</h1>
        <p class="subtitle">Upload and manage your Lua script</p>

        <div class="info">
            <strong>📝 Your Script URL:</strong>
            <code>{{ script_url }}</code>
            <br><br>
            <strong>📋 Loadstring:</strong>
            <code>loadstring(game:HttpGet("{{ script_url }}"))();</code>
        </div>

        <div class="form-group">
            <label>Admin Password:</label>
            <input type="password" id="adminPassword" placeholder="Enter admin password">
        </div>

        <div class="form-group">
            <label>Lua Script Source Code:</label>
            <textarea id="scriptContent" placeholder="Paste your Lua script here...">{{ current_script }}</textarea>
        </div>

        <button onclick="publishScript()">PUBLISH SCRIPT</button>

        <div id="message" class="message"></div>
    </div>

    <script>
        function publishScript() {
            const password = document.getElementById('adminPassword').value;
            const content = document.getElementById('scriptContent').value;
            const message = document.getElementById('message');

            fetch('/api/admin/publish', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    password: password,
                    content: content
                })
            })
            .then(response => response.json())
            .then(data => {
                message.style.display = 'block';
                if (data.success) {
                    message.className = 'message success';
                    message.textContent = '✓ Script published successfully!';
                } else {
                    message.className = 'message error';
                    message.textContent = '✗ ' + data.message;
                }
            })
            .catch(error => {
                message.style.display = 'block';
                message.className = 'message error';
                message.textContent = '✗ Connection error';
            });
        }
    </script>
</body>
</html>
"""

def add_script_hosting_routes(app):
    """Add script hosting routes to the Flask app"""
    
    @app.route('/script')
    def script_page():
        """Serve the password-protected script page"""
        script_url = request.host_url + 'api/script/raw'
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render_template_string(HTML_TEMPLATE, 
                                     script_url=script_url, 
                                     timestamp=timestamp,
                                     discord_invite=DISCORD_INVITE)
    
    @app.route('/admin')
    def admin_page():
        """Serve the admin panel for uploading scripts"""
        script_url = request.host_url + 'api/script/raw'
        return render_template_string(ADMIN_TEMPLATE, 
                                     script_url=script_url,
                                     current_script=SCRIPT_CONTENT)
    
    @app.route('/api/authenticate', methods=['POST'])
    def authenticate():
        """Authenticate password"""
        data = request.get_json()
        password = data.get('password', '')
        
        if password == SCRIPT_PASSWORD:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    
    @app.route('/api/admin/publish', methods=['POST'])
    def publish_script():
        """Publish a new script (admin only)"""
        global SCRIPT_CONTENT
        data = request.get_json()
        password = data.get('password', '')
        content = data.get('content', '')
        
        if password != ADMIN_PASSWORD:
            return jsonify({"success": False, "message": "Invalid admin password"})
        
        if not content or len(content.strip()) == 0:
            return jsonify({"success": False, "message": "Script content cannot be empty"})
        
        SCRIPT_CONTENT = content
        return jsonify({"success": True, "message": "Script published successfully"})
    
    @app.route('/api/script/raw')
    def get_raw_script():
        """Serve the raw Lua script and redirect browser visitors to Discord"""
        user_agent = request.headers.get('User-Agent', '').lower()
        
        # Check if it's a browser (not Roblox/executor)
        is_browser = any(browser in user_agent for browser in ['mozilla', 'chrome', 'safari', 'edge', 'opera'])
        is_roblox = 'roblox' in user_agent or not user_agent
        
        # If it's a browser, redirect to Discord
        if is_browser and not is_roblox:
            return redirect(DISCORD_INVITE)
        
        # Otherwise, serve the script
        return SCRIPT_CONTENT, 200, {'Content-Type': 'text/plain; charset=utf-8'}
