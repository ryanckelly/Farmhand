# Dashboard Deployment Guide

## Overview

The Farmhand Dashboard is deployed as a web application on Railway, making it accessible from any device with a web browser. This document covers the deployment setup, architecture, and maintenance.

## Deployment Platform: Railway

**Live URL**: https://farmhand-production.up.railway.app

### Why Railway?

- Zero-config deployment from GitHub
- Automatic HTTPS/SSL certificates
- Free tier sufficient for personal dashboards
- Auto-deploys on git push
- Built-in environment variable management

## Architecture

### Application Stack

- **Backend**: Flask Python web server (`app.py`)
- **Frontend**: Static HTML/CSS/JavaScript
- **Charts**: Chart.js for interactive visualizations
- **Data Source**: JSON files committed to git repository

### File Structure

```
C:\opt\stardew\
├── app.py                          # Flask web server
├── requirements.txt                # Python dependencies
├── railway.json                    # Railway config (optional)
├── dashboard/
│   ├── dashboard_generator.py     # Dashboard generator
│   ├── dashboard.html             # Main dashboard view
│   ├── trends.html                # Trends page with charts
│   ├── dashboard_state.json       # Dashboard analytics data
│   ├── chart_config.js            # Chart.js configuration
│   └── chart_renderer.js          # Chart rendering logic
├── diary.json                     # Session history
├── metrics.json                   # Trend data
└── save_snapshot.json             # Current game state
```

## Initial Setup

### 1. Create Flask Application

Created `app.py` to serve the dashboard as a web application:

```python
from flask import Flask, send_file, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('dashboard/dashboard.html')

@app.route('/dashboard')
def dashboard():
    return send_file('dashboard/dashboard.html')

@app.route('/trends')
def trends():
    return send_file('dashboard/trends.html')

# Serve static files (JS, JSON)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### 2. Create requirements.txt

```
Flask==3.0.0
```

### 3. Commit Data Files

Railway needs the data files in the repository:

```bash
git add diary.json metrics.json save_snapshot.json
git add dashboard/dashboard_state.json
git commit -m "Add data files for Railway deployment"
git push
```

### 4. Deploy to Railway

1. Sign up at https://railway.app
2. Create new project from GitHub repository
3. Railway auto-detects Python + Flask
4. Deployment starts automatically
5. Domain assigned: `farmhand-production.up.railway.app`

### 5. Configure Routes

Updated navigation links in `dashboard_generator.py` to use Railway-friendly routes:

- `/dashboard` → Main dashboard
- `/trends` → Trends page with charts

## Mobile Responsiveness

### CSS Improvements

The dashboard was optimized for mobile viewing:

1. **Removed ASCII Box Characters**: Replaced text-based borders with CSS borders for proper responsive scaling
2. **Dynamic Sizing**: Used `clamp()` for font sizes and percentage-based widths
3. **Centered Content**: All containers centered with equal margins
4. **Consistent Widths**: All divs use matching `max-width: 800px` and `width: 95%`

Key CSS patterns:

```css
.dashboard-container {
    margin: 0 auto 20px auto;
    max-width: 800px;
    width: 95%;
    padding: 20px;
    box-sizing: border-box;
    border: 3px solid #00ff00;
    border-radius: 8px;
    font-size: clamp(10px, 2.5vw, 14px);
    text-align: center;
}
```

## Updating the Dashboard

### Automatic Updates

Railway auto-deploys when you push to GitHub:

1. Play Stardew Valley and end your session
2. Run `python session_tracker.py` locally
3. Regenerate dashboard: `python dashboard/dashboard_generator.py --with-trends`
4. Commit and push:
   ```bash
   git add dashboard/*.html dashboard/dashboard_state.json diary.json
   git commit -m "Update dashboard data"
   git push
   ```
5. Railway detects push and redeploys (~60 seconds)

### Manual Updates

If you need to manually trigger a deployment:
1. Go to Railway dashboard
2. Select the Farmhand project
3. Click "Deploy" → "Redeploy"

## Monitoring

### Railway Dashboard

- View logs in real-time
- Monitor build status
- Check resource usage (CPU, memory, bandwidth)

### Health Checks

- **Dashboard URL**: https://farmhand-production.up.railway.app/dashboard
- **Trends URL**: https://farmhand-production.up.railway.app/trends

If either returns 404 or 500, check Railway logs for errors.

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure `requirements.txt` lists all dependencies and is committed to git.

### Issue: Data not updating

**Solution**:
1. Verify data files are committed to git
2. Check Railway logs for file read errors
3. Ensure file paths in `app.py` are correct

### Issue: Mobile display issues

**Solution**:
1. Test locally first: open `dashboard/dashboard.html` in browser
2. Use browser dev tools to test mobile viewport
3. Check CSS for fixed widths or non-responsive units

### Issue: Charts not loading

**Solution**:
1. Verify Chart.js CDN is accessible: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`
2. Check browser console for JavaScript errors
3. Ensure `chart_config.js` and `chart_renderer.js` are served correctly

## Cost

Railway provides 500 hours/month of usage on the free tier, which is sufficient for a personal dashboard accessed occasionally. Upgrade to Hobby plan ($5/month) if you exceed free tier limits.

## Security Considerations

- Dashboard is **public** (no authentication)
- Contains game progress data only (no personal information)
- HTTPS enabled by default via Railway
- No sensitive data exposed (save file paths, system info, etc.)

**Note**: If you want to restrict access, consider:
- Railway's private networking (Hobby plan required)
- Adding basic auth to Flask app
- Using Railway environment variables for credentials

## Future Enhancements

Potential improvements for the deployment:

1. **Database Backend**: Store diary/metrics in PostgreSQL instead of JSON files
2. **Real-time Updates**: WebSocket connection to push updates without page refresh
3. **Authentication**: Add login system for private access
4. **API Endpoints**: Expose REST API for third-party integrations
5. **Custom Domain**: Use personal domain instead of Railway subdomain

## References

- [Railway Documentation](https://docs.railway.app/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
