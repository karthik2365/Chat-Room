# Render Deployment Guide

## Quick Deploy Steps:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Go to Render Dashboard:**
   - Visit https://render.com and sign in
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository: `karthik2365/Chat-Room`
   - Render will detect `render.yaml` and set everything up automatically

3. **Configure Environment Variables (Auto-configured via render.yaml):**
   - `SECRET_KEY` - Auto-generated
   - `DATABASE_URL` - Auto-configured from PostgreSQL
   - `ALLOWED_HOSTS` - Add your Render domain (e.g., `yourapp.onrender.com`)
   - `DEBUG` - Set to `False`

4. **Deploy:**
   - Render will automatically build and deploy
   - Database migrations run automatically
   - Access your app at: `https://yourapp.onrender.com`

## Manual Setup (Alternative):

If you prefer manual setup instead of Blueprint:

1. Create PostgreSQL Database:
   - Name: `securechat-db`

2. Create Web Service:
   - Build Command: `./build.sh`
   - Start Command: `daphne -b 0.0.0.0 -p $PORT securechat_backend.asgi:application`
   - Add Environment Variables listed above

## Important Notes:

- **WebSocket Support:** Render supports WebSockets on all plans
- **Free Tier:** Service spins down after 15 mins of inactivity
- **Database:** PostgreSQL is used in production (SQLite locally)
- **Static Files:** WhiteNoise serves static files
- **SSL:** Automatically provided by Render

## After Deployment:

1. Create superuser:
   ```bash
   # In Render Shell
   python manage.py createsuperuser
   ```

2. Access admin: `https://yourapp.onrender.com/admin/`

## Local Testing:

Test production settings locally:
```bash
export DEBUG=False
export SECRET_KEY=your-secret-key
export ALLOWED_HOSTS=localhost,127.0.0.1
python manage.py collectstatic --no-input
daphne -b 127.0.0.1 -p 8000 securechat_backend.asgi:application
```
