#!/usr/bin/env python3
"""
Flask Web Application for Stardew Valley Farmhand Dashboard
Serves the dashboard on Railway.app
"""

import json
import os
from pathlib import Path
from flask import Flask, render_template_string, send_from_directory, jsonify, request, send_file
from datetime import datetime
import sys

# Add current directory to path to import dashboard modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import dashboard generator
from dashboard.dashboard_generator import DashboardGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Base path for data files
BASE_PATH = Path(__file__).parent


@app.route('/')
def index():
    """Home page - redirect to dashboard"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Farmhand Dashboard</title>
        <style>
            body {
                background: #1e1e1e;
                color: #00ff00;
                font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
                padding: 20px;
                margin: 0;
                line-height: 1.6;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
                padding: 40px 20px;
            }
            h1 {
                color: #ffd700;
                font-size: 32px;
                margin-bottom: 20px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            .subtitle {
                color: #00ff00;
                font-size: 16px;
                margin-bottom: 40px;
            }
            .nav-links {
                display: flex;
                flex-direction: column;
                gap: 15px;
                max-width: 400px;
                margin: 0 auto;
            }
            .nav-link {
                background: rgba(0, 255, 0, 0.1);
                border: 2px solid #00ff00;
                color: #00ff00;
                padding: 15px 30px;
                text-decoration: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
                transition: all 0.3s;
                display: block;
            }
            .nav-link:hover {
                background: rgba(0, 255, 0, 0.2);
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
                color: #ffd700;
            }
            .status {
                margin-top: 40px;
                padding: 20px;
                background: rgba(0, 0, 0, 0.3);
                border: 2px solid #00ff00;
                border-radius: 4px;
            }
            .status-item {
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid rgba(0, 255, 0, 0.2);
            }
            .status-item:last-child {
                border-bottom: none;
            }
            .status-label {
                color: #ffd700;
            }
            .status-value {
                color: #00ff00;
            }
            .footer {
                margin-top: 60px;
                padding-top: 20px;
                border-top: 1px solid rgba(0, 255, 0, 0.3);
                font-size: 12px;
                color: rgba(0, 255, 0, 0.6);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>╔═══ Farmhand Dashboard ═══╗</h1>
            <p class="subtitle">Stardew Valley Progress Tracker</p>

            <div class="nav-links">
                <a href="/dashboard" class="nav-link">[ MAIN DASHBOARD ]</a>
                <a href="/trends" class="nav-link">[ TRENDS & ANALYTICS ]</a>
                <a href="/api/status" class="nav-link">[ API STATUS ]</a>
                <a href="/api/refresh" class="nav-link">[ REFRESH DATA ]</a>
            </div>

            <div class="status">
                <div class="status-item">
                    <span class="status-label">Status:</span>
                    <span class="status-value">ONLINE</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Server Time:</span>
                    <span class="status-value" id="serverTime">Loading...</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Version:</span>
                    <span class="status-value">1.0.0</span>
                </div>
            </div>

            <div class="footer">
                Powered by Flask & Railway |
                <a href="https://github.com" style="color: #00ff00; text-decoration: none;">GitHub</a>
            </div>
        </div>

        <script>
            // Update server time
            document.getElementById('serverTime').textContent = new Date().toLocaleString();
            setInterval(() => {
                document.getElementById('serverTime').textContent = new Date().toLocaleString();
            }, 1000);
        </script>
    </body>
    </html>
    '''


@app.route('/dashboard')
def dashboard():
    """Serve the main dashboard HTML"""
    try:
        dashboard_path = BASE_PATH / 'dashboard' / 'dashboard.html'
        if dashboard_path.exists():
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return jsonify({'error': 'Dashboard not generated yet', 'hint': 'Visit /api/refresh to generate'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/trends')
def trends():
    """Serve the trends page HTML"""
    try:
        trends_path = BASE_PATH / 'dashboard' / 'trends.html'
        if trends_path.exists():
            with open(trends_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return jsonify({'error': 'Trends page not generated yet', 'hint': 'Visit /api/refresh to generate'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dashboard/<path:filename>')
def dashboard_files(filename):
    """Serve static files from dashboard directory"""
    return send_from_directory(BASE_PATH / 'dashboard', filename)


@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    try:
        # Check if required files exist
        files_status = {
            'save_snapshot.json': (BASE_PATH / 'save_snapshot.json').exists(),
            'diary.json': (BASE_PATH / 'diary.json').exists(),
            'metrics.json': (BASE_PATH / 'metrics.json').exists(),
            'dashboard_state.json': (BASE_PATH / 'dashboard' / 'dashboard_state.json').exists(),
            'dashboard.html': (BASE_PATH / 'dashboard' / 'dashboard.html').exists(),
            'trends.html': (BASE_PATH / 'dashboard' / 'trends.html').exists()
        }

        # Load dashboard state if available
        dashboard_state = None
        dashboard_state_path = BASE_PATH / 'dashboard' / 'dashboard_state.json'
        if dashboard_state_path.exists():
            with open(dashboard_state_path, 'r', encoding='utf-8') as f:
                dashboard_state = json.load(f)

        return jsonify({
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'files': files_status,
            'all_required_files_present': all([
                files_status['save_snapshot.json'],
                files_status['diary.json'],
                files_status['metrics.json']
            ]),
            'dashboard_generated': files_status['dashboard.html'],
            'last_generated': dashboard_state.get('generated_at') if dashboard_state else None,
            'game_date': dashboard_state.get('game_date') if dashboard_state else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/refresh', methods=['GET', 'POST'])
def api_refresh():
    """API endpoint to regenerate dashboard from existing data"""
    try:
        # Check if required files exist
        required_files = ['save_snapshot.json', 'diary.json', 'metrics.json']
        missing_files = [f for f in required_files if not (BASE_PATH / f).exists()]

        if missing_files:
            return jsonify({
                'error': 'Missing required data files',
                'missing': missing_files,
                'hint': 'Upload your save data files or run session_tracker.py locally first'
            }), 400

        # Generate dashboard
        generator = DashboardGenerator(base_path=str(BASE_PATH))
        generator.load_all_data()
        state = generator.generate_state()

        # Generate HTML files
        html_path = generator.render_html(state, 'dashboard.html')
        trends_path = generator.render_trends_page(state, use_chartjs=True)

        return jsonify({
            'status': 'success',
            'message': 'Dashboard regenerated successfully',
            'generated_at': state['generated_at'],
            'game_date': state['game_date'],
            'files_created': [
                'dashboard/dashboard.html',
                'dashboard/trends.html',
                'dashboard/dashboard_state.json'
            ],
            'links': {
                'dashboard': '/dashboard',
                'trends': '/trends',
                'status': '/api/status'
            }
        })
    except FileNotFoundError as e:
        return jsonify({'error': f'File not found: {str(e)}'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to generate dashboard: {str(e)}'}), 500


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint to upload JSON data files"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        # Validate filename (must be one of the expected JSON files)
        allowed_files = ['save_snapshot.json', 'diary.json', 'metrics.json']
        if file.filename not in allowed_files:
            return jsonify({
                'error': 'Invalid filename',
                'allowed_files': allowed_files
            }), 400

        # Save file
        file_path = BASE_PATH / file.filename
        file.save(str(file_path))

        # Validate JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            file_path.unlink()  # Delete invalid file
            return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

        return jsonify({
            'status': 'success',
            'message': f'File {file.filename} uploaded successfully',
            'next_step': 'Visit /api/refresh to regenerate the dashboard'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    """Custom 404 page"""
    return jsonify({'error': 'Not found', 'hint': 'Visit / for available routes'}), 404


@app.errorhandler(500)
def server_error(e):
    """Custom 500 page"""
    return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


if __name__ == '__main__':
    # Get port from environment (Railway provides PORT)
    port = int(os.environ.get('PORT', 5000))

    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
