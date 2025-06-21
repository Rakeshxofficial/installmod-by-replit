# Quick Heroku Deployment Fix

## The Error You're Seeing
Heroku failed because it needs specific configuration files with exact formats.

## Files I've Fixed/Created:

### 1. ✅ runtime.txt (Fixed)
Changed from `python-3.9` to `python-3.11.9` (Heroku's required format)

### 2. ✅ Procfile (Fixed) 
Changed to: `web: gunicorn main:app`

### 3. ✅ heroku-requirements.txt (New)
Complete dependency list for Heroku

### 4. ✅ app.json (New)
Heroku app configuration with PostgreSQL addon

## Quick Fix Steps:

1. **Replace requirements.txt in your repository:**
   - Delete the existing `requirements.txt`
   - Rename `heroku-requirements.txt` to `requirements.txt`

2. **Commit the changes:**
   ```bash
   git add .
   git commit -m "Fix Heroku deployment files"
   git push origin main
   ```

3. **Deploy to Heroku:**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## Automatic Setup (Alternative)
Use the one-click deploy button with `app.json`:
- Push to GitHub with these files
- Visit: `https://heroku.com/deploy?template=https://github.com/YOUR_USERNAME/REPO_NAME`

## After Deployment:
- Set environment variables:
  ```bash
  heroku config:set SESSION_SECRET="random-secret-key"
  heroku config:set BASE_DOMAIN="installmod.com"
  ```
- Import your data:
  ```bash
  heroku pg:psql < your_backup.sql
  ```

Your subdomain system will work on Heroku with proper DNS configuration.