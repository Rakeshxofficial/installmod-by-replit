# Subdomain Implementation Setup Guide

## Overview
Your Flask application now implements a subdomain system where:
- App detail pages: `big-small-predictor.installmod.com`
- Game detail pages: `whatsapp-mod.installmod.com`
- News articles remain: `installmod.com/news-article-slug`

## Implementation Features

### ✅ Completed Features
1. **Subdomain Routing**: Automatic detection and serving of content from subdomains
2. **301 Redirects**: Old URLs like `/app-slug` redirect to `app-slug.installmod.com`
3. **Canonical Tags**: Properly set to subdomain URLs for SEO
4. **Sitemap Updates**: All app/game URLs now use subdomain format
5. **Meta Tag Support**: Custom meta titles and descriptions work on subdomains

### How It Works
1. User visits old URL: `installmod.com/big-small-predictor`
2. System detects it's an app/game → 301 redirect to subdomain
3. New URL: `big-small-predictor.installmod.com`
4. Subdomain routing serves the app detail page
5. Canonical tag points to subdomain URL

## Vercel Deployment Requirements

### 1. DNS Configuration (Required)
Add wildcard CNAME record in your domain registrar:
```
Type: CNAME
Name: *
Value: installmod.com
TTL: 3600
```

### 2. Vercel Domain Setup
In Vercel dashboard, add these domains:
- `installmod.com`
- `www.installmod.com`
- `*.installmod.com` (wildcard for all subdomains)

### 3. Environment Variables
Set in Vercel:
- `BASE_DOMAIN=installmod.com`
- `DATABASE_URL=your_database_url`

### 4. Database Migration
Since Vercel doesn't support PostgreSQL natively:
1. Export current data: `pg_dump $DATABASE_URL > backup.sql`
2. Set up external PostgreSQL (Neon, Supabase, PlanetScale)
3. Import data to new database
4. Update DATABASE_URL in Vercel

## Testing Subdomain System

### Local Testing (Limited)
On localhost, subdomain detection is disabled for development.

### Production Testing
Once deployed:
1. Visit old URL: `installmod.com/app-slug`
2. Should redirect to: `app-slug.installmod.com`
3. Check canonical tag in page source
4. Verify sitemap shows subdomain URLs

## SEO Benefits
- Each app/game gets its own domain authority
- Better keyword targeting in URLs
- Improved site structure for search engines
- Clean separation of content types

## Files Modified
- `app.py`: Subdomain routing logic
- `templates/base.html`: Canonical tag system
- `templates/sitemap_clean.xml`: Subdomain URLs
- `vercel.json`: Deployment configuration
- `templates/app_detail.html`: Canonical URL logic
- `templates/game_detail.html`: Canonical URL logic

Your subdomain system is now ready for deployment!