#!/usr/bin/env python3
"""
Automated update and deployment script
Runs session tracker, generates dashboard, and uploads to Railway
"""

import subprocess
import sys
import os
from pathlib import Path
import requests


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n[*] {description}...")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} completed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def upload_files(base_url):
    """Upload data files to Railway"""
    print("\n[*] Uploading data files to Railway...")

    base_url = base_url.rstrip('/')
    data_files = ['save_snapshot.json', 'diary.json', 'metrics.json']

    for filename in data_files:
        try:
            with open(filename, 'rb') as f:
                print(f"  Uploading {filename}...", end=" ")
                response = requests.post(
                    f"{base_url}/api/upload",
                    files={'file': (filename, f, 'application/json')},
                    timeout=30
                )

                if response.status_code == 200:
                    print("✅")
                else:
                    print(f"❌ ({response.status_code})")
                    return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    return True


def refresh_dashboard(base_url):
    """Refresh the dashboard on Railway"""
    print("\n[*] Refreshing dashboard...")

    try:
        response = requests.get(f"{base_url.rstrip('/')}/api/refresh", timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dashboard refreshed successfully")
            print(f"   Game Date: {result.get('game_date')}")
            return True
        else:
            print(f"❌ Refresh failed ({response.status_code})")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main automation workflow"""
    print("=" * 70)
    print("AUTOMATED UPDATE & DEPLOYMENT")
    print("=" * 70)

    # Check for Railway URL
    railway_url = os.environ.get('RAILWAY_URL')

    if not railway_url and len(sys.argv) >= 2:
        railway_url = sys.argv[1]

    if not railway_url:
        print("\n❌ Railway URL not provided")
        print("\nUsage:")
        print("  python update_and_deploy.py <railway-url>")
        print("\nOr set environment variable:")
        print("  export RAILWAY_URL=https://your-app.up.railway.app")
        sys.exit(1)

    # Step 1: Run session tracker
    if not run_command([sys.executable, 'session_tracker.py'], "Running session tracker"):
        print("\n❌ Session tracker failed - aborting deployment")
        sys.exit(1)

    # Step 2: Generate dashboard locally (optional - to verify it works)
    print("\n[*] Generating dashboard locally for verification...")
    if Path('dashboard/dashboard_generator.py').exists():
        run_command(
            [sys.executable, 'dashboard/dashboard_generator.py', '--terminal'],
            "Generating dashboard preview"
        )

    # Step 3: Upload to Railway
    if not upload_files(railway_url):
        print("\n❌ Upload failed - aborting deployment")
        sys.exit(1)

    # Step 4: Refresh dashboard
    if not refresh_dashboard(railway_url):
        print("\n❌ Dashboard refresh failed")
        sys.exit(1)

    # Success!
    print("\n" + "=" * 70)
    print("✅ DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Your updated dashboard is live at:")
    print(f"  🌐 Dashboard: {railway_url}/dashboard")
    print(f"  📊 Trends:    {railway_url}/trends")
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()
