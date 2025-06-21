"""Update owner password to new secure password"""
from app import app, db
from models import Admin

def update_owner_password():
    with app.app_context():
        # Get the owner admin
        owner = Admin.query.filter_by(username='admin', is_owner=True).first()
        
        if owner:
            # Set the new password
            new_password = 'Owner1Rakesh62@$#'
            owner.set_password(new_password)
            db.session.commit()
            print("✓ Owner password updated successfully")
        else:
            print("✗ Owner account not found")

if __name__ == '__main__':
    update_owner_password()