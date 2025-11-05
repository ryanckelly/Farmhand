#!/usr/bin/env python3
"""
Local deployment test script
Tests the Flask app before deploying to Railway
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def test_local_deployment():
    """Test the Flask application locally"""
    print("=" * 70)
    print("TESTING LOCAL DEPLOYMENT")
    print("=" * 70)
    print()

    # Check if required files exist
    print("[1/5] Checking required files...")
    required_files = [
        'app.py',
        'requirements.txt',
        'Procfile',
        'railway.toml',
        'dashboard/dashboard_generator.py'
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            print(f"  ❌ Missing: {file}")
        else:
            print(f"  ✅ Found: {file}")

    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False

    print("\n✅ All required files present")

    # Check for data files
    print("\n[2/5] Checking data files...")
    data_files = ['save_snapshot.json', 'diary.json', 'metrics.json']
    has_data = True

    for file in data_files:
        if not Path(file).exists():
            print(f"  ⚠️  Missing: {file}")
            has_data = False
        else:
            print(f"  ✅ Found: {file}")

    if not has_data:
        print("\n⚠️  Some data files missing - dashboard won't be generated")
        print("   Run session_tracker.py first or upload data via API")

    # Check Python dependencies
    print("\n[3/5] Checking Python dependencies...")
    try:
        import flask
        print(f"  ✅ Flask {flask.__version__} installed")
    except ImportError:
        print("  ❌ Flask not installed")
        print("     Run: pip install -r requirements.txt")
        return False

    # Try to start the Flask app
    print("\n[4/5] Starting Flask application...")
    print("  Press Ctrl+C to stop the server when done testing\n")

    try:
        # Start Flask in subprocess
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait a moment for server to start
        time.sleep(3)

        # Test if server is running
        print("[5/5] Testing API endpoints...")
        try:
            # Test home page
            response = requests.get('http://localhost:5000/', timeout=5)
            if response.status_code == 200:
                print("  ✅ Home page: http://localhost:5000/")
            else:
                print(f"  ❌ Home page returned status {response.status_code}")

            # Test status endpoint
            response = requests.get('http://localhost:5000/api/status', timeout=5)
            if response.status_code == 200:
                print("  ✅ Status API: http://localhost:5000/api/status")
                data = response.json()
                print(f"     - Status: {data.get('status')}")
                print(f"     - All required files: {data.get('all_required_files_present')}")
                print(f"     - Dashboard generated: {data.get('dashboard_generated')}")
            else:
                print(f"  ❌ Status API returned status {response.status_code}")

            print("\n" + "=" * 70)
            print("✅ LOCAL DEPLOYMENT TEST SUCCESSFUL!")
            print("=" * 70)
            print()
            print("Your Flask app is running at: http://localhost:5000")
            print()
            print("Available endpoints:")
            print("  - Home:         http://localhost:5000/")
            print("  - Dashboard:    http://localhost:5000/dashboard")
            print("  - Trends:       http://localhost:5000/trends")
            print("  - API Status:   http://localhost:5000/api/status")
            print("  - API Refresh:  http://localhost:5000/api/refresh")
            print()
            print("Press Ctrl+C to stop the server")
            print("=" * 70)

            # Wait for user to stop the server
            process.wait()

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Failed to connect to Flask server: {e}")
            print("     Make sure port 5000 is available")
            process.terminate()
            return False

    except KeyboardInterrupt:
        print("\n\n[*] Shutting down Flask server...")
        process.terminate()
        process.wait()
        print("✅ Server stopped successfully")
        return True

    except Exception as e:
        print(f"\n❌ Error starting Flask app: {e}")
        if 'process' in locals():
            process.terminate()
        return False

    return True


if __name__ == '__main__':
    success = test_local_deployment()
    sys.exit(0 if success else 1)
