#!/bin/bash
# Heroku Deployment Script for installMOD

echo "🚀 Preparing Heroku Deployment..."

# Step 1: Replace requirements.txt
echo "📦 Updating requirements.txt for Heroku..."
if [ -f "heroku-requirements.txt" ]; then
    cp heroku-requirements.txt requirements.txt
    echo "✅ Requirements updated"
else
    echo "❌ heroku-requirements.txt not found"
    exit 1
fi

# Step 2: Verify critical files exist
echo "🔍 Checking deployment files..."
for file in "runtime.txt" "Procfile" "app.json" "requirements.txt"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Step 3: Git operations
echo "📝 Committing changes..."
git add .
git commit -m "Fix Heroku deployment configuration"

# Step 4: Heroku deployment
echo "🌐 Deploying to Heroku..."
echo "Run these commands manually:"
echo ""
echo "heroku create installmod-website"
echo "heroku addons:create heroku-postgresql:essential-0"
echo "heroku config:set SESSION_SECRET=\"$(openssl rand -base64 32)\""
echo "heroku config:set BASE_DOMAIN=\"installmod.com\""
echo "git push heroku main"
echo ""
echo "🎯 Your app will be live at: https://installmod-website.herokuapp.com"
echo "📊 Configure custom domain: heroku domains:add installmod.com"