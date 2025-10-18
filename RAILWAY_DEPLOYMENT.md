# Railway Deployment Guide for Alpha Learning Platform

This guide will walk you through deploying the Alpha Learning Platform to Railway.app.

## Prerequisites

- A Railway account (sign up at [railway.app](https://railway.app))
- Git installed on your computer
- The Alpha Learning Platform code

## Overview

Railway will host two services:
1. **Backend** - Flask API server
2. **Frontend** - React application

## Step-by-Step Deployment

### Step 1: Prepare Your Project

1. **Download the project** from the sandbox or ensure you have it on your local machine

2. **Initialize Git repository** (if not already done):
```bash
cd alpha-learning-platform
git init
git add .
git commit -m "Initial commit"
```

3. **Push to GitHub** (recommended) or GitLab:
```bash
# Create a new repository on GitHub, then:
git remote add origin https://github.com/your-username/alpha-learning-platform.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy the Backend

1. **Log in to Railway**
   - Go to [railway.app](https://railway.app)
   - Click "Login" and sign in with GitHub

2. **Create a New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `alpha-learning-platform` repository
   - Railway will detect it's a monorepo

3. **Configure Backend Service**
   - Click "Add Service" → "GitHub Repo"
   - Select your repository
   - Set the **Root Directory** to: `backend`
   - Railway will auto-detect it's a Python project

4. **Set Environment Variables**
   - Click on your backend service
   - Go to "Variables" tab
   - Add the following variables:

   ```
   SECRET_KEY=your-random-secret-key-here-make-it-long-and-random
   JWT_SECRET_KEY=another-random-secret-key-for-jwt-tokens
   PORT=5000
   ```

   To generate secure keys, you can use:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Deploy**
   - Railway will automatically build and deploy
   - Wait for deployment to complete (usually 2-3 minutes)
   - Copy the generated URL (e.g., `https://backend-production-xxxx.up.railway.app`)

### Step 3: Initialize the Database

1. **Access the Railway CLI** or use the web terminal:
   - In your backend service, go to "Settings" → "Service"
   - Or install Railway CLI locally:
   ```bash
   npm install -g @railway/cli
   railway login
   railway link
   ```

2. **Run the database initialization**:
   ```bash
   railway run python init_db.py
   ```

   This will create test users:
   - Student: `student1` / `password123`
   - Teacher: `teacher1` / `password123`
   - Parent: `parent1` / `password123`
   - Admin: `admin1` / `password123`

### Step 4: Deploy the Frontend

1. **Add Frontend Service**
   - In your Railway project, click "New Service"
   - Select "GitHub Repo" again
   - Choose the same repository
   - Set the **Root Directory** to: `frontend`

2. **Set Environment Variables**
   - Click on your frontend service
   - Go to "Variables" tab
   - Add:

   ```
   VITE_API_URL=https://your-backend-url.up.railway.app/api
   ```

   Replace `your-backend-url` with the actual backend URL from Step 2.

3. **Configure Build Settings**
   - Railway will auto-detect the Node.js project
   - Build Command: `npm run build` (auto-detected)
   - Start Command: `npm run preview -- --host 0.0.0.0 --port $PORT`

4. **Deploy**
   - Railway will build and deploy the frontend
   - Wait for deployment to complete
   - Copy the generated URL (e.g., `https://frontend-production-xxxx.up.railway.app`)

### Step 5: Update CORS Settings

1. **Update Backend CORS** (if needed):
   - Go to your backend service variables
   - Add:
   ```
   FRONTEND_URL=https://your-frontend-url.up.railway.app
   ```

2. **Redeploy backend** if you made changes

### Step 6: Test Your Application

1. **Access your frontend URL**
2. **Try logging in** with test credentials:
   - Username: `student1`
   - Password: `password123`

3. **Test different user roles**:
   - Student Portal
   - Teacher Portal
   - Parent Portal
   - Admin Panel

## Troubleshooting

### Backend Issues

**Build fails:**
- Check that `requirements.txt` includes all dependencies
- Verify Python version (should be 3.11+)

**Database errors:**
- Make sure you ran `init_db.py`
- Check Railway logs for specific errors

**500 errors:**
- Check environment variables are set correctly
- Review Railway logs: Service → Deployments → View Logs

### Frontend Issues

**API connection errors:**
- Verify `VITE_API_URL` is set correctly
- Make sure it includes `/api` at the end
- Check CORS settings on backend

**Build fails:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check for any environment-specific code

**Blank page:**
- Check browser console for errors
- Verify the build completed successfully
- Check Railway deployment logs

## Updating Your Application

### Update Backend:
```bash
git add backend/
git commit -m "Update backend"
git push
```
Railway will automatically redeploy.

### Update Frontend:
```bash
git add frontend/
git commit -m "Update frontend"
git push
```
Railway will automatically rebuild and redeploy.

## Cost Considerations

Railway offers:
- **Free tier**: $5 credit per month
- **Hobby plan**: $5/month + usage
- **Pro plan**: $20/month + usage

For a small application like this:
- Backend: ~$3-5/month
- Frontend: ~$2-3/month
- Total: ~$5-8/month

The free tier should be sufficient for testing and light usage.

## Custom Domain (Optional)

1. Go to your frontend service settings
2. Click "Settings" → "Domains"
3. Click "Custom Domain"
4. Add your domain and follow DNS instructions

## Database Backup

Railway doesn't provide automatic SQLite backups. For production:

1. **Consider upgrading to PostgreSQL**:
   - Add PostgreSQL service in Railway
   - Update backend to use PostgreSQL
   - Railway provides automatic backups

2. **Manual SQLite backup**:
   - Use Railway CLI to download database:
   ```bash
   railway run python -c "import shutil; shutil.copy('instance/alpha_learning.db', 'backup.db')"
   ```

## Security Recommendations

1. **Change default secrets** in environment variables
2. **Enable HTTPS** (Railway does this automatically)
3. **Set up proper CORS** with specific frontend URL
4. **Regular backups** of your database
5. **Monitor logs** for suspicious activity

## Support

If you encounter issues:
1. Check Railway documentation: [docs.railway.app](https://docs.railway.app)
2. Review deployment logs in Railway dashboard
3. Check browser console for frontend errors
4. Verify all environment variables are set correctly

## Next Steps

After successful deployment:
1. Create real user accounts
2. Add actual educational content
3. Customize branding and styling
4. Set up monitoring and analytics
5. Consider adding email notifications
6. Implement proper database backup strategy

Your Alpha Learning Platform is now live and accessible to users worldwide!

