#!/usr/bin/env python3
"""
Upload data files to Railway deployment
Uploads save_snapshot.json, diary.json, and metrics.json to your Railway app
"""

import requests
import sys
from pathlib import Path
import json


def upload_to_railway(base_url):
    """
    Upload all data files to Railway and refresh the dashboard

    Args:
        base_url: Your Railway app URL (e.g., https://your-app.up.railway.app)
    """
    print("=" * 70)
    print("UPLOADING DATA TO RAILWAY")
    print("=" * 70)
    print()

    # Remove trailing slash from URL if present
    base_url = base_url.rstrip('/')

    # Files to upload
    data_files = ['save_snapshot.json', 'diary.json', 'metrics.json']

    # Check if files exist locally
    print("[1/3] Checking local data files...")
    missing_files = []
    for filename in data_files:
        if not Path(filename).exists():
            missing_files.append(filename)
            print(f"  [X] Missing: {filename}")
        else:
            # Check if valid JSON
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"  [OK] Valid: {filename}")
            except json.JSONDecodeError as e:
                print(f"  [X] Invalid JSON in {filename}: {e}")
                missing_files.append(filename)

    if missing_files:
        print(f"\n[ERROR] Missing or invalid files: {', '.join(missing_files)}")
        print("   Run session_tracker.py first to generate these files")
        return False

    # Upload files
    print("\n[2/3] Uploading files to Railway...")
    uploaded = 0

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
                    result = response.json()
                    print(f"[OK] {result.get('status', 'success')}")
                    uploaded += 1
                else:
                    print(f"[ERROR] Status {response.status_code}")
                    try:
                        error = response.json()
                        print(f"     {error.get('error', 'Unknown error')}")
                    except:
                        print(f"     {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Connection error: {e}")
        except Exception as e:
            print(f"[ERROR] {e}")

    if uploaded == 0:
        print("\n[ERROR] No files uploaded successfully")
        return False

    print(f"\n[SUCCESS] Uploaded {uploaded}/{len(data_files)} files")

    # Refresh dashboard
    print("\n[3/3] Refreshing dashboard...")
    try:
        response = requests.get(f"{base_url}/api/refresh", timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"  [OK] Status: {result.get('status')}")
            print(f"  Game Date: {result.get('game_date')}")
            print(f"  Generated: {result.get('generated_at')}")
        else:
            print(f"  [ERROR] Status {response.status_code}")
            try:
                error = response.json()
                print(f"     {error.get('error', 'Unknown error')}")
            except:
                print(f"     {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Connection error: {e}")
        return False

    # Success!
    print("\n" + "=" * 70)
    print("[SUCCESS] DEPLOYMENT SUCCESSFUL!")
    print("=" * 70)
    print()
    print("Your dashboard is now live at:")
    print(f"  Dashboard: {base_url}/dashboard")
    print(f"  Trends:    {base_url}/trends")
    print(f"  API:       {base_url}/api/status")
    print()
    print("=" * 70)

    return True


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python upload_to_railway.py <railway-url>")
        print()
        print("Example:")
        print("  python upload_to_railway.py https://your-app.up.railway.app")
        print()
        print("Get your Railway URL from:")
        print("  - Railway dashboard > Settings > Domains")
        print("  - Or run: railway domain")
        sys.exit(1)

    base_url = sys.argv[1]

    # Validate URL format
    if not base_url.startswith(('http://', 'https://')):
        print(f"❌ Invalid URL: {base_url}")
        print("   URL must start with http:// or https://")
        sys.exit(1)

    success = upload_to_railway(base_url)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
