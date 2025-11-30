# Deploy to Render - Step by Step Guide

## Prerequisites
1. GitHub account
2. Render account (sign up at https://render.com - free tier available)

## Step 1: Push Code to GitHub

1. **Initialize Git** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit - Ready for Render deployment"
```

2. **Create a GitHub repository**:
   - Go to https://github.com/new
   - Create a new repository (e.g., "auto-invoice-generator")
   - Don't initialize with README

3. **Push your code**:
```bash
git remote add origin https://github.com/YOUR_USERNAME/auto-invoice-generator.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Render

1. **Sign in to Render**:
   - Go to https://render.com
   - Sign up/Login (you can use GitHub to sign in)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account if not already connected
   - Select your repository: `auto-invoice-generator`

3. **Configure Service**:
   - **Name**: `invoice-generator` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `.` if needed)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

4. **Environment Variables**:
   - Click "Add Environment Variable"
   - **Key**: `SECRET_KEY`
   - **Value**: Generate a random secret key (you can use: `python -c "import secrets; print(secrets.token_hex(32))"`)

5. **Plan**:
   - Select "Free" plan (or paid if you prefer)
   - Free plan has limitations but works for testing

6. **Deploy**:
   - Click "Create Web Service"
   - Render will start building and deploying your app
   - Wait 5-10 minutes for first deployment

## Step 3: Verify Deployment

1. Once deployed, Render will give you a URL like: `https://invoice-generator.onrender.com`
2. Visit the URL to see your app
3. The database will be created automatically on first run

## Important Notes

- **Free Tier Limitations**:
  - Service spins down after 15 minutes of inactivity
  - First request after spin-down may take 30-60 seconds
  - Consider upgrading to paid plan for production use

- **Database**:
  - SQLite database will be created in the `instance/` folder
  - Data persists between deployments
  - For production, consider using PostgreSQL (Render provides free PostgreSQL)

- **Logo File**:
  - Make sure `logo.png` is in the root directory
  - It will be included in the deployment

- **Environment Variables**:
  - `SECRET_KEY` is required for production
  - Render will auto-generate it if you use `render.yaml`

## Troubleshooting

If deployment fails:
1. Check build logs in Render dashboard
2. Ensure all dependencies are in `requirements.txt`
3. Verify `Procfile` exists and is correct
4. Check that `app.py` has `app = create_app()` at module level

## Updating Your App

After making changes:
1. Commit and push to GitHub
2. Render will automatically redeploy
3. Or manually trigger redeploy from Render dashboard

