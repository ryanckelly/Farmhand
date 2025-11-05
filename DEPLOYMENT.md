# Deploying Farmhand Dashboard to Railway

This guide will help you deploy the Stardew Valley Farmhand Dashboard to Railway.app for web access.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app) (free tier available)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, or Bitbucket)
3. **Railway CLI** (optional): Install for local testing
   ```bash
   npm install -g @railway/cli
   ```

## Quick Deploy (GitHub)

### Option 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

2. **Connect to Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect the Python app and deploy

3. **Configure Environment Variables** (Optional)
   - In Railway dashboard, go to your project
   - Click "Variables" tab
   - Add:
     - `SECRET_KEY`: A random secret key for Flask (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
     - `FLASK_ENV`: Set to `production`

4. **Access Your Dashboard**
   - Railway will provide a URL like `https://your-app.up.railway.app`
   - Visit the URL to see your dashboard!

### Option 2: Deploy with Railway CLI

1. **Login to Railway**
   ```bash
   railway login
   ```

2. **Initialize Railway Project**
   ```bash
   railway init
   ```

3. **Deploy**
   ```bash
   railway up
   ```

4. **Open in Browser**
   ```bash
   railway open
   ```

## Project Structure

```
stardew/
├── app.py                      # Flask web application
├── requirements.txt            # Python dependencies
├── Procfile                    # Railway start command
├── railway.toml                # Railway configuration
├── .railwayignore             # Files to exclude from deployment
├── dashboard/
│   ├── dashboard_generator.py  # Dashboard logic
│   ├── dashboard.html         # Main dashboard page
│   ├── trends.html            # Trends page
│   ├── chart_config.js        # Chart.js configuration
│   └── chart_renderer.js      # Chart rendering
├── save_snapshot.json         # Game save data (upload via API)
├── diary.json                 # Session history (upload via API)
└── metrics.json               # Trend data (upload via API)
```

## API Endpoints

Your deployed dashboard will have these endpoints:

### Web Pages
- `GET /` - Home page with navigation
- `GET /dashboard` - Main dashboard view
- `GET /trends` - Trends & analytics page

### API Endpoints
- `GET /api/status` - Check system status and data files
- `GET /api/refresh` - Regenerate dashboard from existing data
- `POST /api/upload` - Upload JSON data files (save_snapshot.json, diary.json, metrics.json)

## Uploading Your Data

Since your save files are local, you'll need to upload them to Railway:

### Method 1: Using curl (Command Line)

```bash
# Upload save_snapshot.json
curl -F "file=@save_snapshot.json" https://your-app.up.railway.app/api/upload

# Upload diary.json
curl -F "file=@diary.json" https://your-app.up.railway.app/api/upload

# Upload metrics.json
curl -F "file=@metrics.json" https://your-app.up.railway.app/api/upload

# Refresh the dashboard
curl https://your-app.up.railway.app/api/refresh
```

### Method 2: Using Python

```python
import requests

base_url = "https://your-app.up.railway.app"

# Upload files
files_to_upload = ["save_snapshot.json", "diary.json", "metrics.json"]

for filename in files_to_upload:
    with open(filename, 'rb') as f:
        response = requests.post(
            f"{base_url}/api/upload",
            files={'file': (filename, f, 'application/json')}
        )
        print(f"{filename}: {response.json()}")

# Refresh dashboard
response = requests.get(f"{base_url}/api/refresh")
print("Refresh:", response.json())
```

### Method 3: Include Data in Deployment

If you want your data deployed with the app:

1. **Edit `.railwayignore`** and comment out these lines:
   ```
   # save_snapshot.json
   # diary.json
   # metrics.json
   ```

2. **Commit and push**:
   ```bash
   git add save_snapshot.json diary.json metrics.json .railwayignore
   git commit -m "Include game data in deployment"
   git push
   ```

3. Railway will redeploy automatically with your data included

## Local Testing

Test the deployment locally before pushing to Railway:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask app**
   ```bash
   python app.py
   ```
   Or with Gunicorn (production server):
   ```bash
   gunicorn app:app --bind 0.0.0.0:5000 --workers 2
   ```

3. **Visit in browser**
   ```
   http://localhost:5000
   ```

4. **Test API endpoints**
   ```bash
   # Check status
   curl http://localhost:5000/api/status

   # Refresh dashboard
   curl http://localhost:5000/api/refresh
   ```

## Continuous Deployment

Railway supports automatic deployments from Git:

1. **Enable Auto-Deploy**
   - In Railway dashboard, go to your project
   - Click "Settings"
   - Enable "Auto Deploy" for your main branch

2. **Update Your Dashboard**
   - Make changes locally
   - Run `session_tracker.py` to update data
   - Commit and push changes
   - Railway automatically redeploys!

## Automation Script

Create a helper script to update and deploy:

```python
# update_and_deploy.py
import subprocess
import requests
import os

# 1. Run session tracker
print("[1/4] Running session tracker...")
subprocess.run(["python", "session_tracker.py"], check=True)

# 2. Generate fresh dashboard
print("[2/4] Generating dashboard...")
subprocess.run(["python", "dashboard/dashboard_generator.py"], check=True)

# 3. Upload to Railway
print("[3/4] Uploading data to Railway...")
base_url = os.environ.get("RAILWAY_URL", "https://your-app.up.railway.app")

for filename in ["save_snapshot.json", "diary.json", "metrics.json"]:
    with open(filename, 'rb') as f:
        response = requests.post(
            f"{base_url}/api/upload",
            files={'file': (filename, f, 'application/json')}
        )
        print(f"  {filename}: {response.json()['status']}")

# 4. Refresh dashboard
print("[4/4] Refreshing dashboard...")
response = requests.get(f"{base_url}/api/refresh")
print(f"  Dashboard: {response.json()['status']}")

print("\n✅ Deployment complete! Visit your dashboard at:")
print(f"   {base_url}/dashboard")
```

Run with:
```bash
python update_and_deploy.py
```

## Troubleshooting

### "Application failed to respond"
- Check Railway logs in the dashboard
- Verify `PORT` environment variable is being used
- Make sure Gunicorn is installed in requirements.txt

### "Dashboard not generated yet"
- Visit `/api/status` to check if data files exist
- Upload your JSON files using the API
- Visit `/api/refresh` to generate the dashboard

### "Missing required data files"
- You need to upload `save_snapshot.json`, `diary.json`, and `metrics.json`
- Use the upload API endpoint or include them in deployment

### "Internal server error"
- Check Railway logs for Python errors
- Make sure all Python dependencies are in requirements.txt
- Verify dashboard_generator.py works locally

## Environment Variables

Optional environment variables you can set in Railway:

- `SECRET_KEY`: Flask secret key (auto-generated if not set)
- `FLASK_ENV`: Set to `production` for production mode
- `PORT`: Railway sets this automatically
- `NIXPACKS_PYTHON_VERSION`: Python version (default: 3.11)

## Cost Estimation

Railway free tier includes:
- $5 credit per month
- Includes 500 hours of runtime
- 1GB memory
- 1GB disk space

This should be more than enough for a personal dashboard!

## Security Considerations

1. **API Access**: Currently, the API is public. Consider adding authentication:
   - Use Flask-HTTPAuth for basic auth
   - Add API key validation
   - Use Railway environment variables for credentials

2. **File Uploads**: The upload endpoint only accepts specific JSON files
   - Validates JSON format
   - Restricts to allowed filenames
   - Consider adding size limits

3. **Secret Key**: Set a strong SECRET_KEY in Railway environment variables

## Next Steps

1. **Custom Domain**: Add a custom domain in Railway settings
2. **Add Authentication**: Protect your dashboard with a password
3. **Scheduled Updates**: Use Railway cron jobs to auto-refresh data
4. **Monitoring**: Set up Railway monitoring and alerts

## Support

- Railway Docs: https://docs.railway.app
- Flask Docs: https://flask.palletsprojects.com
- GitHub Issues: [Your repo URL]

Happy farming! 🌾
