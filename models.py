from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    is_owner = db.Column(db.Boolean, default=False)  # Owner/Super Admin flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    apps = db.relationship('App', backref='admin_author', lazy=True, cascade='all, delete-orphan')
    games = db.relationship('Game', backref='admin_author', lazy=True, cascade='all, delete-orphan')
    news = db.relationship('News', backref='admin_author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'

class App(db.Model):
    __tablename__ = 'apps'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    version = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    icon = db.Column(db.Text)
    description = db.Column(db.Text)
    features = db.Column(db.Text)  # JSON string
    category = db.Column(db.String(50))
    featured = db.Column(db.String(50))
    download_count = db.Column(db.String(20))
    rating = db.Column(db.Float)
    votes = db.Column(db.Integer)
    screenshots = db.Column(db.Text)  # JSON string
    featured_image = db.Column(db.Text)
    short_description = db.Column(db.Text)
    publisher = db.Column(db.String(200))
    genre = db.Column(db.String(100))
    mod_info = db.Column(db.String(200))
    last_updated = db.Column(db.String(50))
    mod_features = db.Column(db.Text)  # JSON string
    whats_new_title = db.Column(db.String(200))
    whats_new_content = db.Column(db.Text)
    article_sections = db.Column(db.Text)  # JSON string
    download_link = db.Column(db.Text)  # Download URL for the app
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)  # Content owner
    
    # Advanced SEO Settings
    meta_title = db.Column(db.String(300), nullable=True)  # Custom meta title
    meta_description = db.Column(db.Text, nullable=True)  # Custom meta description
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for template compatibility"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'version': self.version,
            'size': self.size,
            'icon': self.icon,
            'description': self.description,
            'features': json.loads(self.features) if self.features else [],
            'category': self.category,
            'featured': self.featured,
            'download_count': self.download_count,
            'rating': self.rating,
            'votes': self.votes,
            'screenshots': json.loads(self.screenshots) if self.screenshots else [],
            'featured_image': self.featured_image,
            'short_description': self.short_description,
            'publisher': self.publisher,
            'genre': self.genre,
            'mod_info': self.mod_info,
            'last_updated': self.last_updated,
            'mod_features': json.loads(self.mod_features) if self.mod_features else [],
            'whats_new': {
                'title': self.whats_new_title,
                'content': self.whats_new_content
            } if self.whats_new_title else None,
            'article_sections': self.article_sections or '',
            'download_link': self.download_link,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description
        }

class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    version = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    icon = db.Column(db.Text)
    description = db.Column(db.Text)
    features = db.Column(db.Text)  # JSON string
    category = db.Column(db.String(50))
    featured = db.Column(db.String(50))
    download_count = db.Column(db.String(20))
    rating = db.Column(db.Float)
    votes = db.Column(db.Integer)
    screenshots = db.Column(db.Text)  # JSON string
    featured_image = db.Column(db.Text)
    short_description = db.Column(db.Text)
    publisher = db.Column(db.String(200))
    genre = db.Column(db.String(100))
    mod_info = db.Column(db.String(200))
    last_updated = db.Column(db.String(50))
    article_sections = db.Column(db.Text)  # Markdown content
    download_link = db.Column(db.Text)  # Download URL for the game
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)  # Content owner
    
    # Advanced SEO Settings
    meta_title = db.Column(db.String(300), nullable=True)  # Custom meta title
    meta_description = db.Column(db.Text, nullable=True)  # Custom meta description
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for template compatibility"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'version': self.version,
            'size': self.size,
            'icon': self.icon,
            'description': self.description,
            'features': json.loads(self.features) if self.features else [],
            'category': self.category,
            'featured': self.featured,
            'download_count': self.download_count,
            'rating': self.rating,
            'votes': self.votes,
            'screenshots': json.loads(self.screenshots) if self.screenshots else [],
            'featured_image': self.featured_image,
            'short_description': self.short_description,
            'publisher': self.publisher,
            'genre': self.genre,
            'mod_info': self.mod_info,
            'last_updated': self.last_updated,
            'article_sections': self.article_sections,
            'download_link': self.download_link,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description
        }

class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False)
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text)
    featured_image = db.Column(db.Text)
    author = db.Column(db.String(100))
    date = db.Column(db.String(50))
    category = db.Column(db.String(50))
    tags = db.Column(db.Text)  # JSON string
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)  # Content owner
    
    # Advanced SEO Settings
    meta_title = db.Column(db.String(300), nullable=True)  # Custom meta title
    meta_description = db.Column(db.Text, nullable=True)  # Custom meta description
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for template compatibility"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'content': self.content,
            'featured_image': self.featured_image,
            'author': self.author,
            'date': self.date,
            'category': self.category,
            'tags': json.loads(self.tags) if self.tags else [],
            'meta_title': self.meta_title,
            'meta_description': self.meta_description
        }

class Download(db.Model):
    __tablename__ = 'downloads'
    
    id = db.Column(db.Integer, primary_key=True)
    app_slug = db.Column(db.String(200), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    download_date = db.Column(db.DateTime, default=datetime.utcnow)
    
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    app_slug = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=True)
    
    # Relationship to replies
    replies = db.relationship('Reply', backref='parent_comment', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'app_slug': self.app_slug,
            'name': self.name,
            'email': self.email,
            'text': self.text,
            'date': self.date.strftime('%B %d, %Y'),
            'approved': self.approved,
            'replies': [reply.to_dict() for reply in self.replies]
        }

class Reply(db.Model):
    __tablename__ = 'replies'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'comment_id': self.comment_id,
            'name': self.name,
            'email': self.email,
            'text': self.text,
            'date': self.date.strftime('%B %d, %Y'),
            'approved': self.approved
        }

class SearchQuery(db.Model):
    __tablename__ = 'search_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    search_term = db.Column(db.String(200), unique=True, nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    search_count = db.Column(db.Integer, default=1)
    first_searched = db.Column(db.DateTime, default=datetime.utcnow)
    last_searched = db.Column(db.DateTime, default=datetime.utcnow)
    results_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<SearchQuery {self.search_term}>'


class Ad(db.Model):
    __tablename__ = 'ads'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Markdown content
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, default=1)  # Higher number = higher priority
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    admin = db.relationship('Admin', backref='ads', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'is_active': self.is_active,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Ad {self.title}>'


class AdView(db.Model):
    __tablename__ = 'ad_views'
    
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('ads.id'), nullable=False)
    user_ip = db.Column(db.String(45), nullable=False)  # Support IPv6
    view_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    ad = db.relationship('Ad', backref='views', lazy=True)
    
    # Unique constraint to ensure one view per user per ad per day
    __table_args__ = (
        db.UniqueConstraint('ad_id', 'user_ip', 'view_date', name='unique_ad_view_per_day'),
    )
    
    def __repr__(self):
        return f'<AdView ad_id={self.ad_id} ip={self.user_ip} date={self.view_date}>'