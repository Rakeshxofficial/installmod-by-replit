# Heroku Deployment Guide for installMOD

## Quick Fix for Your Current Error

The error you're seeing is because Heroku needs specific files. I've just created/fixed:

1. ✅ `runtime.txt` - Fixed to use `python-3.11.9`
2. ✅ `requirements.txt` - Created with all dependencies
3. ✅ `Procfile` - Fixed for Heroku
4. ✅ `app.json` - Added for easy deployment

## Deploy to Heroku (Easiest Method)

### Option 1: One-Click Deploy
1. Push the updated files to your GitHub repository
2. Use this deploy button in your README:

```markdown
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
```

### Option 2: Manual Deployment

```bash
# Install Heroku CLI first, then:
heroku login
heroku create installmod-website
heroku addons:create heroku-postgresql:essential-0
git push heroku main
```

## Set Environment Variables

```bash
# Required environment variables
heroku config:set SESSION_SECRET="your-random-secret-key"
heroku config:set BASE_DOMAIN="installmod.com"

# Database URL is automatically set by Heroku Postgres addon
```

## Import Your Existing Data

```bash
# Export from current database
pg_dump $DATABASE_URL > installmod_backup.sql

# Import to Heroku database
heroku pg:psql < installmod_backup.sql
```

## Configure Custom Domain (After Deployment)

```bash
# Add your domain to Heroku
heroku domains:add installmod.com
heroku domains:add www.installmod.com
heroku domains:add *.installmod.com

# Get DNS target from Heroku
heroku domains
```

Then update your DNS records:
```
CNAME: installmod.com → your-app-name.herokuapp.com
CNAME: www.installmod.com → your-app-name.herokuapp.com  
CNAME: *.installmod.com → your-app-name.herokuapp.com
```

## Expected Results

After successful deployment:
- Main site: `https://your-app-name.herokuapp.com`
- With custom domain: `https://installmod.com`
- Subdomains: `https://app-slug.installmod.com`
- Old URLs redirect: `/app-slug` → `app-slug.installmod.com`

## Troubleshooting

### Build Errors
- Ensure `requirements.txt` lists all dependencies
- Check `runtime.txt` has correct Python version
- Verify `Procfile` syntax is correct

### Database Issues
- Heroku Postgres addon provides DATABASE_URL automatically
- Use `heroku pg:info` to check database status
- Import data with `heroku pg:psql < backup.sql`

### Domain Issues
- Verify DNS propagation (up to 48 hours)
- Check domain configuration with `heroku domains`
- Ensure wildcard domain `*.installmod.com` is configured

Your Flask app with subdomain system is now ready for Heroku deployment!