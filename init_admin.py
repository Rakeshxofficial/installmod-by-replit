"""Initialize admin system with default account"""
import os
from app import app, db
from models import Admin, App, Game, News

def init_admin_system():
    """Initialize admin system and create default admin account"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if default admin exists
        default_admin = Admin.query.filter_by(username='admin').first()
        
        if not default_admin:
            # Create default admin account
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            default_admin = Admin()
            default_admin.username = 'admin'
            default_admin.email = 'admin@installmod.com'
            default_admin.full_name = 'Default Administrator'
            default_admin.is_active = True
            default_admin.set_password(admin_password)
            
            db.session.add(default_admin)
            db.session.commit()
            
            print(f"✓ Default admin created: username='admin', password='{admin_password}'")
            
            # Assign orphaned content to default admin
            orphaned_apps = App.query.filter_by(admin_id=None).all()
            orphaned_games = Game.query.filter_by(admin_id=None).all()
            orphaned_news = News.query.filter_by(admin_id=None).all()
            
            for app_item in orphaned_apps:
                app_item.admin_id = default_admin.id
            for game in orphaned_games:
                game.admin_id = default_admin.id
            for news in orphaned_news:
                news.admin_id = default_admin.id
            
            if orphaned_apps or orphaned_games or orphaned_news:
                db.session.commit()
                print(f"✓ Assigned {len(orphaned_apps)} apps, {len(orphaned_games)} games, {len(orphaned_news)} news to default admin")
        
        else:
            print("✓ Admin system already initialized")

if __name__ == '__main__':
    init_admin_system()