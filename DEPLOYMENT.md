# Deployment Guide for installMOD

## Important Database Considerations

Your Flask application uses PostgreSQL with persistent data storage. **Vercel's serverless functions are stateless and don't support persistent PostgreSQL databases** - they're designed for stateless applications.

## Recommended Deployment Options

### 1. **Replit Deployments (Recommended)**
- ✅ Built-in PostgreSQL database support
- ✅ Automatic SSL/HTTPS
- ✅ Zero configuration needed
- ✅ Your database and environment are already configured

**To deploy on Replit:**
1. Click the "Deploy" button in your Replit dashboard
2. Your app will be automatically deployed with database intact

### 2. **Heroku (Good Alternative)**
- ✅ Excellent PostgreSQL support with Heroku Postgres
- ✅ Easy Python/Flask deployment
- ✅ Automatic database migrations

**Setup for Heroku:**
```bash
# Install Heroku CLI and login
pip install gunicorn
echo "web: gunicorn main:app" > Procfile
```

### 3. **Railway (Modern Alternative)**
- ✅ Built-in PostgreSQL
- ✅ Simple deployment from GitHub
- ✅ Automatic HTTPS

### 4. **DigitalOcean App Platform**
- ✅ Managed PostgreSQL databases
- ✅ Easy scaling
- ✅ Good performance

## Vercel Limitations

While I've created Vercel configuration files for you, be aware:
- ❌ No built-in database - you'd need external PostgreSQL (like Neon, PlanetScale)
- ❌ Serverless functions have execution time limits
- ❌ Cold starts can affect performance
- ❌ More complex database migration process

## Files Created for Vercel (if you still want to try)

1. `vercel.json` - Vercel configuration
2. `api/index.py` - Serverless function entry point
3. `runtime.txt` - Python version specification
4. `.vercelignore` - Files to exclude from deployment

## Database Migration Required for Vercel

If you choose Vercel, you'll need:
1. External PostgreSQL service (Neon, Supabase, etc.)
2. Export your current data: `pg_dump $DATABASE_URL > backup.sql`
3. Import to new database
4. Update DATABASE_URL environment variable

## Recommendation

**Use Replit Deployments** - it's the simplest option since your database and environment are already configured. Your app will be live with one click while maintaining all your data and admin accounts.