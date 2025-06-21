#!/usr/bin/env python3
"""
Setup script for multi-admin system
Creates default admin account and initializes database
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask app and database
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash
from datetime import datetime

# Create Flask app instance for setup
class Base(DeclarativeBase):
    pass

setup_app = Flask(__name__)
setup_app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
setup_app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
setup_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

setup_db = SQLAlchemy(setup_app, model_class=Base)

# Admin model for setup
class Admin(setup_db.Model):
    __tablename__ = 'admins'
    
    id = setup_db.Column(setup_db.Integer, primary_key=True)
    username = setup_db.Column(setup_db.String(80), unique=True, nullable=False)
    email = setup_db.Column(setup_db.String(120), unique=True, nullable=False)
    password_hash = setup_db.Column(setup_db.String(256), nullable=False)
    full_name = setup_db.Column(setup_db.String(200))
    is_active = setup_db.Column(setup_db.Boolean, default=True)
    created_at = setup_db.Column(setup_db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

def setup_default_admin():
    """Create default admin account"""
    with setup_app.app_context():
        # Create tables
        setup_db.create_all()
        
        # Check if default admin exists
        default_admin = Admin.query.filter_by(username='admin').first()
        
        if not default_admin:
            # Create default admin
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            default_admin = Admin(
                username='admin',
                email='admin@installmod.com',
                full_name='Default Administrator',
                is_active=True
            )
            default_admin.set_password(admin_password)
            
            db.session.add(default_admin)
            db.session.commit()
            
            print(f"✓ Default admin created: username='admin', password='{admin_password}'")
            
            # Update existing content to belong to default admin
            from models import App, Game, News
            
            # Assign orphaned content to default admin
            orphaned_apps = App.query.filter_by(admin_id=None).all()
            orphaned_games = Game.query.filter_by(admin_id=None).all()
            orphaned_news = News.query.filter_by(admin_id=None).all()
            
            for app in orphaned_apps:
                app.admin_id = default_admin.id
            for game in orphaned_games:
                game.admin_id = default_admin.id
            for news in orphaned_news:
                news.admin_id = default_admin.id
            
            db.session.commit()
            
            print(f"✓ Assigned {len(orphaned_apps)} apps, {len(orphaned_games)} games, {len(orphaned_news)} news to default admin")
        else:
            print("✓ Default admin already exists")

def create_new_admin(username, email, password, full_name=None):
    """Create a new admin account"""
    with app.app_context():
        # Check if admin exists
        existing_admin = Admin.query.filter(
            (Admin.username == username) | (Admin.email == email)
        ).first()
        
        if existing_admin:
            print(f"✗ Admin with username '{username}' or email '{email}' already exists")
            return False
        
        # Create new admin
        new_admin = Admin(
            username=username,
            email=email,
            full_name=full_name or username,
            is_active=True
        )
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"✓ New admin created: username='{username}', email='{email}'")
        return True

if __name__ == '__main__':
    print("Setting up multi-admin system...")
    setup_default_admin()
    print("Setup complete!")