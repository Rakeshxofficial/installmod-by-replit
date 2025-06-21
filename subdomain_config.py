"""
Subdomain Configuration for Vercel Deployment

This file contains the configuration needed for subdomain routing on Vercel.
For production deployment, you'll need to configure DNS wildcard records.

Required DNS Configuration:
1. Add a CNAME record: *.installmod.com → installmod.com
2. Configure Vercel custom domains to handle wildcard subdomains

Environment Variables needed:
- BASE_DOMAIN: your main domain (e.g., installmod.com)

How it works:
1. User visits old URL like /app-slug → 301 redirect to app-slug.installmod.com
2. Subdomain requests are handled by the subdomain routing logic
3. Canonical tags point to subdomain URLs for SEO
4. Sitemap generates subdomain URLs for all apps/games
"""

# Example DNS configuration for your domain registrar:
DNS_RECORDS = {
    "Type": "CNAME",
    "Name": "*",
    "Value": "installmod.com",
    "TTL": "3600"
}

# Vercel domains configuration
VERCEL_DOMAINS = [
    "installmod.com",
    "www.installmod.com", 
    "*.installmod.com"  # Wildcard for all subdomains
]