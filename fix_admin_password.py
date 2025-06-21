"""Fix admin password for login"""
from app import app, db
from models import Admin
from werkzeug.security import generate_password_hash

def fix_admin_password():
    with app.app_context():
        # Get the admin user
        admin = Admin.query.filter_by(username='admin').first()
        
        if admin:
            # Set the password properly
            admin.password_hash = generate_password_hash('admin123')
            db.session.commit()
            print("✓ Admin password updated successfully")
        else:
            # Create new admin if doesn't exist
            admin = Admin()
            admin.username = 'admin'
            admin.email = 'admin@installmod.com'
            admin.full_name = 'Default Administrator'
            admin.is_active = True
            admin.password_hash = generate_password_hash('admin123')
            
            db.session.add(admin)
            db.session.commit()
            print("✓ New admin account created")

if __name__ == '__main__':
    fix_admin_password()