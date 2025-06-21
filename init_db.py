#!/usr/bin/env python3
"""Initialize database and migrate existing JSON data"""

import os
import json
from app import app
from models import db, App, Game, News

def load_json_data(filename):
    """Load JSON data from the data directory"""
    try:
        with open(f'data/{filename}', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Data file {filename} not found")
        return []

def migrate_apps():
    """Migrate apps from JSON to database"""
    apps_data = load_json_data('apps.json')
    print(f"Migrating {len(apps_data)} apps...")
    
    for app_data in apps_data:
        # Check if app already exists
        existing_app = App.query.filter_by(slug=app_data.get('slug')).first()
        if existing_app:
            continue
            
        app = App(
            name=app_data.get('name'),
            slug=app_data.get('slug'),
            version=app_data.get('version'),
            size=app_data.get('size'),
            icon=app_data.get('icon'),
            description=app_data.get('description'),
            features=json.dumps(app_data.get('features', [])),
            category=app_data.get('category'),
            featured=app_data.get('featured'),
            download_count=app_data.get('download_count'),
            rating=app_data.get('rating'),
            votes=app_data.get('votes'),
            screenshots=json.dumps(app_data.get('screenshots', [])),
            featured_image=app_data.get('featured_image'),
            short_description=app_data.get('short_description'),
            publisher=app_data.get('publisher'),
            genre=app_data.get('genre'),
            mod_info=app_data.get('mod_info'),
            last_updated=app_data.get('last_updated'),
            mod_features=json.dumps(app_data.get('mod_features', [])),
            whats_new_title=app_data.get('whats_new', {}).get('title') if app_data.get('whats_new') else None,
            whats_new_content=app_data.get('whats_new', {}).get('content') if app_data.get('whats_new') else None,
            article_sections=json.dumps(app_data.get('article_sections', []))
        )
        db.session.add(app)
    
    db.session.commit()
    print("Apps migration completed")

def migrate_games():
    """Migrate games from JSON to database"""
    games_data = load_json_data('games.json')
    print(f"Migrating {len(games_data)} games...")
    
    for game_data in games_data:
        # Check if game already exists
        existing_game = Game.query.filter_by(slug=game_data.get('slug')).first()
        if existing_game:
            continue
            
        game = Game(
            name=game_data.get('name'),
            slug=game_data.get('slug'),
            version=game_data.get('version'),
            size=game_data.get('size'),
            icon=game_data.get('icon'),
            description=game_data.get('description'),
            features=json.dumps(game_data.get('features', [])),
            category=game_data.get('category'),
            featured=game_data.get('featured'),
            download_count=game_data.get('download_count'),
            rating=game_data.get('rating'),
            votes=game_data.get('votes'),
            screenshots=json.dumps(game_data.get('screenshots', [])),
            featured_image=game_data.get('featured_image'),
            short_description=game_data.get('short_description'),
            publisher=game_data.get('publisher'),
            genre=game_data.get('genre'),
            mod_info=game_data.get('mod_info'),
            last_updated=game_data.get('last_updated')
        )
        db.session.add(game)
    
    db.session.commit()
    print("Games migration completed")

def migrate_news():
    """Migrate news from JSON to database"""
    news_data = load_json_data('news.json')
    print(f"Migrating {len(news_data)} news articles...")
    
    for article_data in news_data:
        # Check if article already exists
        existing_article = News.query.filter_by(slug=article_data.get('slug')).first()
        if existing_article:
            continue
            
        article = News(
            title=article_data.get('title'),
            slug=article_data.get('slug'),
            excerpt=article_data.get('excerpt'),
            content=article_data.get('content'),
            featured_image=article_data.get('featured_image'),
            author=article_data.get('author'),
            date=article_data.get('date'),
            category=article_data.get('category'),
            tags=json.dumps(article_data.get('tags', []))
        )
        db.session.add(article)
    
    db.session.commit()
    print("News migration completed")

def init_database():
    """Initialize database with tables and migrate data"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created")
        
        # Migrate existing JSON data
        migrate_apps()
        migrate_games()
        migrate_news()
        
        print("Database initialization completed!")

if __name__ == '__main__':
    init_database()