import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, App, Game, News, Comment, Reply, Admin, Ad, AdView
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin.login'))
        
        # Verify admin still exists and is active
        admin = Admin.query.get(session['admin_id'])
        if not admin or not admin.is_active:
            session.clear()
            return redirect(url_for('admin.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_admin():
    """Get the currently logged-in admin"""
    if 'admin_id' in session:
        return Admin.query.get(session['admin_id'])
    return None

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin.login'))
        
        current_admin = get_current_admin()
        if not current_admin or not current_admin.is_owner:
            flash('Access denied. Owner privileges required.', 'error')
            return redirect(url_for('admin.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            admin = Admin.query.filter_by(username=username, is_active=True).first()
            if admin and admin.check_password(password):
                session['admin_id'] = admin.id
                session['admin_username'] = admin.username
                session['admin_name'] = admin.full_name or admin.username
                flash(f'Welcome back, {admin.full_name or admin.username}!', 'success')
                return redirect(url_for('admin.dashboard'))
        
        flash('Invalid credentials or account disabled!', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    current_admin = get_current_admin()
    
    # Get counts for current admin's content only
    apps_count = App.query.filter_by(admin_id=current_admin.id).count()
    games_count = Game.query.filter_by(admin_id=current_admin.id).count()
    news_count = News.query.filter_by(admin_id=current_admin.id).count()
    
    # Get recent items for current admin only
    recent_apps = App.query.filter_by(admin_id=current_admin.id).order_by(App.created_at.desc()).limit(5).all()
    recent_games = Game.query.filter_by(admin_id=current_admin.id).order_by(Game.created_at.desc()).limit(5).all()
    recent_news = News.query.filter_by(admin_id=current_admin.id).order_by(News.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         apps_count=apps_count,
                         games_count=games_count,
                         news_count=news_count,
                         recent_apps=recent_apps,
                         recent_games=recent_games,
                         recent_news=recent_news,
                         current_admin=current_admin)

# Apps Management
@admin_bp.route('/apps')
@admin_required
def apps_list():
    """List current admin's apps only"""
    current_admin = get_current_admin()
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = App.query.filter_by(admin_id=current_admin.id)
    if search:
        query = query.filter(App.name.contains(search))
    
    apps = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/apps_list.html', apps=apps, search=search, current_admin=current_admin)

@admin_bp.route('/apps/add', methods=['GET', 'POST'])
@admin_required
def add_app():
    """Add new app"""
    current_admin = get_current_admin()
    
    if request.method == 'POST':
        app = App(
            name=request.form.get('name'),
            slug=request.form.get('slug'),
            version=request.form.get('version'),
            size=request.form.get('size'),
            icon=request.form.get('icon'),
            description=request.form.get('description'),
            features=json.dumps([f.strip() for f in request.form.get('features', '').strip().split('\n') if f.strip()] if request.form.get('features', '').strip() else []),
            category=request.form.get('category'),
            featured=request.form.get('featured'),
            download_count=request.form.get('download_count'),
            rating=float(request.form.get('rating', 0)),
            votes=int(request.form.get('votes', 0)),
            screenshots=json.dumps([s.strip() for s in request.form.get('screenshots', '').strip().split('\n') if s.strip()] if request.form.get('screenshots', '').strip() else []),
            featured_image=request.form.get('featured_image'),
            short_description=request.form.get('short_description'),
            publisher=request.form.get('publisher'),
            genre=request.form.get('genre'),
            mod_info=request.form.get('mod_info'),
            last_updated=request.form.get('last_updated'),
            mod_features=json.dumps([f.strip() for f in request.form.get('mod_features', '').strip().split('\n') if f.strip()] if request.form.get('mod_features', '').strip() else []),
            whats_new_title=request.form.get('whats_new_title'),
            whats_new_content=request.form.get('whats_new_content'),
            article_sections=request.form.get('article_content', ''),
            download_link=request.form.get('download_link'),
            meta_title=request.form.get('meta_title', '').strip() or None,
            meta_description=request.form.get('meta_description', '').strip() or None,
            admin_id=current_admin.id  # Assign to current admin
        )
        
        try:
            db.session.add(app)
            db.session.commit()
            flash('App added successfully!', 'success')
            return redirect(url_for('admin.apps_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding app: {str(e)}', 'error')
    
    return render_template('admin/app_form.html', app=None, action='Add', current_admin=current_admin)

@admin_bp.route('/apps/edit/<int:app_id>', methods=['GET', 'POST'])
@admin_required
def edit_app(app_id):
    """Edit existing app"""
    current_admin = get_current_admin()
    # Allow owner to edit all apps, regular admins only their own
    if current_admin.is_owner:
        app = App.query.get_or_404(app_id)
    else:
        app = App.query.filter_by(id=app_id, admin_id=current_admin.id).first_or_404()
    
    if request.method == 'POST':
        app.name = request.form.get('name')
        app.slug = request.form.get('slug')
        app.version = request.form.get('version')
        app.size = request.form.get('size')
        app.icon = request.form.get('icon')
        app.description = request.form.get('description')
        # Process features with proper filtering
        features_text = request.form.get('features', '').strip()
        app.features = json.dumps([f.strip() for f in features_text.split('\n') if f.strip()] if features_text else [])
        
        app.category = request.form.get('category')
        app.featured = request.form.get('featured')
        app.download_count = request.form.get('download_count')
        app.rating = float(request.form.get('rating', 0))
        app.votes = int(request.form.get('votes', 0))
        
        # Process screenshots with proper filtering
        screenshots_text = request.form.get('screenshots', '').strip()
        app.screenshots = json.dumps([s.strip() for s in screenshots_text.split('\n') if s.strip()] if screenshots_text else [])
        
        app.featured_image = request.form.get('featured_image')
        app.short_description = request.form.get('short_description')
        app.publisher = request.form.get('publisher')
        app.genre = request.form.get('genre')
        app.mod_info = request.form.get('mod_info')
        app.last_updated = request.form.get('last_updated')
        
        # Process MOD features with proper filtering
        mod_features_text = request.form.get('mod_features', '').strip()
        app.mod_features = json.dumps([f.strip() for f in mod_features_text.split('\n') if f.strip()] if mod_features_text else [])
        app.whats_new_title = request.form.get('whats_new_title')
        app.whats_new_content = request.form.get('whats_new_content')
        app.article_sections = request.form.get('article_content', '')
        app.download_link = request.form.get('download_link')
        
        # Advanced SEO settings
        meta_title = request.form.get('meta_title', '').strip()
        meta_description = request.form.get('meta_description', '').strip()
        app.meta_title = meta_title if meta_title else None
        app.meta_description = meta_description if meta_description else None
        
        app.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('App updated successfully!', 'success')
            return redirect(url_for('admin.apps_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating app: {str(e)}', 'error')
    
    return render_template('admin/app_form.html', app=app, action='Edit')

@admin_bp.route('/apps/delete/<int:app_id>', methods=['POST'])
@admin_required
def delete_app(app_id):
    """Delete app"""
    current_admin = get_current_admin()
    # Allow owner to delete all apps, regular admins only their own
    if current_admin.is_owner:
        app = App.query.get_or_404(app_id)
    else:
        app = App.query.filter_by(id=app_id, admin_id=current_admin.id).first_or_404()
    
    try:
        db.session.delete(app)
        db.session.commit()
        flash('App deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting app: {str(e)}', 'error')
    
    return redirect(url_for('admin.apps_list'))

# Games Management
@admin_bp.route('/games')
@admin_required
def games_list():
    """List current admin's games only"""
    current_admin = get_current_admin()
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Game.query.filter_by(admin_id=current_admin.id)
    if search:
        query = query.filter(Game.name.contains(search))
    
    games = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/games_list.html', games=games, search=search, current_admin=current_admin)

@admin_bp.route('/games/add', methods=['GET', 'POST'])
@admin_required
def add_game():
    """Add new game"""
    current_admin = get_current_admin()
    
    if request.method == 'POST':
        game = Game(
            name=request.form.get('name'),
            slug=request.form.get('slug'),
            version=request.form.get('version'),
            size=request.form.get('size'),
            icon=request.form.get('icon'),
            description=request.form.get('description'),
            features=json.dumps([f.strip() for f in request.form.get('features', '').strip().split('\n') if f.strip()] if request.form.get('features', '').strip() else []),
            category=request.form.get('category'),
            featured=request.form.get('featured'),
            download_count=request.form.get('download_count'),
            rating=float(request.form.get('rating', 0)),
            votes=int(request.form.get('votes', 0)),
            screenshots=json.dumps([s.strip() for s in request.form.get('screenshots', '').strip().split('\n') if s.strip()] if request.form.get('screenshots', '').strip() else []),
            featured_image=request.form.get('featured_image'),
            short_description=request.form.get('short_description'),
            publisher=request.form.get('publisher'),
            genre=request.form.get('genre'),
            mod_info=request.form.get('mod_info'),
            last_updated=request.form.get('last_updated'),
            article_sections=request.form.get('article_content', ''),
            download_link=request.form.get('download_link'),
            meta_title=request.form.get('meta_title', '').strip() or None,
            meta_description=request.form.get('meta_description', '').strip() or None,
            admin_id=current_admin.id  # Assign to current admin
        )
        
        try:
            db.session.add(game)
            db.session.commit()
            flash('Game added successfully!', 'success')
            return redirect(url_for('admin.games_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding game: {str(e)}', 'error')
    
    return render_template('admin/game_form.html', game=None, action='Add')

@admin_bp.route('/games/edit/<int:game_id>', methods=['GET', 'POST'])
@admin_required
def edit_game(game_id):
    """Edit existing game"""
    game = Game.query.get_or_404(game_id)
    
    if request.method == 'POST':
        game.name = request.form.get('name')
        game.slug = request.form.get('slug')
        game.version = request.form.get('version')
        game.size = request.form.get('size')
        game.icon = request.form.get('icon')
        game.description = request.form.get('description')
        # Process features with proper filtering
        features_text = request.form.get('features', '').strip()
        game.features = json.dumps([f.strip() for f in features_text.split('\n') if f.strip()] if features_text else [])
        
        game.category = request.form.get('category')
        game.featured = request.form.get('featured')
        game.download_count = request.form.get('download_count')
        game.rating = float(request.form.get('rating', 0))
        game.votes = int(request.form.get('votes', 0))
        
        # Process screenshots with proper filtering
        screenshots_text = request.form.get('screenshots', '').strip()
        game.screenshots = json.dumps([s.strip() for s in screenshots_text.split('\n') if s.strip()] if screenshots_text else [])
        game.featured_image = request.form.get('featured_image')
        game.short_description = request.form.get('short_description')
        game.publisher = request.form.get('publisher')
        game.genre = request.form.get('genre')
        game.mod_info = request.form.get('mod_info')
        game.last_updated = request.form.get('last_updated')
        game.article_sections = request.form.get('article_content', '')
        game.download_link = request.form.get('download_link')
        
        # Advanced SEO settings
        meta_title = request.form.get('meta_title', '').strip()
        meta_description = request.form.get('meta_description', '').strip()
        game.meta_title = meta_title if meta_title else None
        game.meta_description = meta_description if meta_description else None
        
        game.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Game updated successfully!', 'success')
            return redirect(url_for('admin.games_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating game: {str(e)}', 'error')
    
    return render_template('admin/game_form.html', game=game, action='Edit')

@admin_bp.route('/games/delete/<int:game_id>', methods=['POST'])
@admin_required
def delete_game(game_id):
    """Delete game"""
    game = Game.query.get_or_404(game_id)
    
    try:
        db.session.delete(game)
        db.session.commit()
        flash('Game deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting game: {str(e)}', 'error')
    
    return redirect(url_for('admin.games_list'))

# News Management
@admin_bp.route('/news')
@admin_required
def news_list():
    """List current admin's news articles only"""
    current_admin = get_current_admin()
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = News.query.filter_by(admin_id=current_admin.id)
    if search:
        query = query.filter(News.title.contains(search))
    
    news = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/news_list.html', news=news, search=search, current_admin=current_admin)

@admin_bp.route('/news/add', methods=['GET', 'POST'])
@admin_required
def add_news():
    """Add new news article"""
    current_admin = get_current_admin()
    
    if request.method == 'POST':
        article = News(
            title=request.form.get('title'),
            slug=request.form.get('slug'),
            excerpt=request.form.get('excerpt'),
            content=request.form.get('content'),
            featured_image=request.form.get('featured_image'),
            author=request.form.get('author'),
            date=request.form.get('date'),
            category=request.form.get('category'),
            tags=json.dumps([tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()] if request.form.get('tags') else []),
            admin_id=current_admin.id  # Assign to current admin
        )
        
        try:
            db.session.add(article)
            db.session.commit()
            flash('News article added successfully!', 'success')
            return redirect(url_for('admin.news_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding news article: {str(e)}', 'error')
    
    return render_template('admin/news_form.html', article=None, action='Add')

@admin_bp.route('/news/edit/<int:news_id>', methods=['GET', 'POST'])
@admin_required
def edit_news(news_id):
    """Edit existing news article"""
    article = News.query.get_or_404(news_id)
    
    if request.method == 'POST':
        article.title = request.form.get('title')
        article.slug = request.form.get('slug')
        article.excerpt = request.form.get('excerpt')
        article.content = request.form.get('content')
        article.featured_image = request.form.get('featured_image')
        article.author = request.form.get('author')
        article.date = request.form.get('date')
        article.category = request.form.get('category')
        article.tags = json.dumps([tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()] if request.form.get('tags') else [])
        
        # Advanced SEO settings
        meta_title = request.form.get('meta_title', '').strip()
        meta_description = request.form.get('meta_description', '').strip()
        article.meta_title = meta_title if meta_title else None
        article.meta_description = meta_description if meta_description else None
        
        article.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('News article updated successfully!', 'success')
            return redirect(url_for('admin.news_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating news article: {str(e)}', 'error')
    
    return render_template('admin/news_form.html', article=article, action='Edit')

@admin_bp.route('/news/delete/<int:news_id>', methods=['POST'])
@admin_required
def delete_news(news_id):
    """Delete news article"""
    article = News.query.get_or_404(news_id)
    
    try:
        db.session.delete(article)
        db.session.commit()
        flash('News article deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting news article: {str(e)}', 'error')
    
    return redirect(url_for('admin.news_list'))

# Categories Management
@admin_bp.route('/categories')
@admin_required
def categories():
    """Manage categories"""
    app_categories = db.session.query(App.category).distinct().all()
    game_categories = db.session.query(Game.category).distinct().all()
    
    app_categories = [cat[0] for cat in app_categories if cat[0]]
    game_categories = [cat[0] for cat in game_categories if cat[0]]
    
    # Calculate counts for each category
    app_category_counts = {}
    for category in app_categories:
        app_category_counts[category] = App.query.filter_by(category=category).count()
    
    game_category_counts = {}
    for category in game_categories:
        game_category_counts[category] = Game.query.filter_by(category=category).count()
    
    return render_template('admin/categories.html', 
                         app_categories=app_categories,
                         game_categories=game_categories,
                         app_category_counts=app_category_counts,
                         game_category_counts=game_category_counts)

# Publishers Management
@admin_bp.route('/publishers')
@admin_required
def publishers():
    """Manage publishers"""
    app_publishers = db.session.query(App.publisher).distinct().all()
    game_publishers = db.session.query(Game.publisher).distinct().all()
    
    app_publishers = [pub[0] for pub in app_publishers if pub[0]]
    game_publishers = [pub[0] for pub in game_publishers if pub[0]]
    
    all_publishers = list(set(app_publishers + game_publishers))
    
    publisher_stats = {}
    for publisher in all_publishers:
        app_count = App.query.filter_by(publisher=publisher).count()
        game_count = Game.query.filter_by(publisher=publisher).count()
        publisher_stats[publisher] = {
            'apps': app_count,
            'games': game_count,
            'total': app_count + game_count
        }
    
    return render_template('admin/publishers.html', 
                         publishers=publisher_stats)

# Comments Management
@admin_bp.route('/comments')
@admin_required
def comments_list():
    """List all comments"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    per_page = 20
    
    query = Comment.query
    
    # Apply search filter
    if search:
        query = query.filter(
            db.or_(
                Comment.name.contains(search),
                Comment.text.contains(search),
                Comment.app_slug.contains(search),
                Comment.email.contains(search)
            )
        )
    
    # Apply status filter
    if status == 'approved':
        query = query.filter(Comment.approved == True)
    elif status == 'pending':
        query = query.filter(Comment.approved == False)
    
    comments = query.order_by(Comment.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get app/game names for each comment
    for comment in comments.items:
        app = App.query.filter_by(slug=comment.app_slug).first()
        if app:
            comment.app_name = app.name
            comment.app_type = 'App'
        else:
            game = Game.query.filter_by(slug=comment.app_slug).first()
            if game:
                comment.app_name = game.name
                comment.app_type = 'Game'
            else:
                comment.app_name = comment.app_slug
                comment.app_type = 'Unknown'
    
    return render_template('admin/comments.html', 
                         comments=comments,
                         search=search,
                         status=status)

@admin_bp.route('/comments/delete/<int:comment_id>', methods=['POST'])
@admin_required
def delete_comment(comment_id):
    """Delete comment"""
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        # Delete all replies first (due to foreign key constraint)
        Reply.query.filter_by(comment_id=comment_id).delete()
        
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting comment: {str(e)}', 'error')
    
    return redirect(url_for('admin.comments_list'))

@admin_bp.route('/comments/toggle-approval/<int:comment_id>', methods=['POST'])
@admin_required
def toggle_comment_approval(comment_id):
    """Toggle comment approval status"""
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        comment.approved = not comment.approved
        db.session.commit()
        
        status = 'approved' if comment.approved else 'hidden'
        flash(f'Comment {status} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating comment: {str(e)}', 'error')
    
    return redirect(url_for('admin.comments_list'))

@admin_bp.route('/comments/bulk-action', methods=['POST'])
@admin_required
def bulk_comment_action():
    """Bulk action for comments"""
    action = request.form.get('action')
    comment_ids = request.form.getlist('comment_ids')
    
    if not comment_ids:
        flash('No comments selected!', 'error')
        return redirect(url_for('admin.comments_list'))
    
    try:
        if action == 'delete':
            # Delete replies first
            Reply.query.filter(Reply.comment_id.in_(comment_ids)).delete(synchronize_session=False)
            # Delete comments
            Comment.query.filter(Comment.id.in_(comment_ids)).delete(synchronize_session=False)
            flash(f'{len(comment_ids)} comments deleted successfully!', 'success')
        elif action == 'approve':
            Comment.query.filter(Comment.id.in_(comment_ids)).update({'approved': True}, synchronize_session=False)
            flash(f'{len(comment_ids)} comments approved successfully!', 'success')
        elif action == 'hide':
            Comment.query.filter(Comment.id.in_(comment_ids)).update({'approved': False}, synchronize_session=False)
            flash(f'{len(comment_ids)} comments hidden successfully!', 'success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Error performing bulk action: {str(e)}', 'error')
    
    return redirect(url_for('admin.comments_list'))

# API endpoints for AJAX operations
@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """Get dashboard statistics"""
    return jsonify({
        'apps': App.query.count(),
        'games': Game.query.count(),
        'news': News.query.count(),
        'comments': Comment.query.count(),
        'pending_comments': Comment.query.filter_by(approved=False).count(),
        'categories': {
            'apps': len(set([cat[0] for cat in db.session.query(App.category).distinct().all() if cat[0]])),
            'games': len(set([cat[0] for cat in db.session.query(Game.category).distinct().all() if cat[0]]))
        },
        'publishers': len(set([pub[0] for pub in db.session.query(App.publisher).distinct().all() if pub[0]] + 
                            [pub[0] for pub in db.session.query(Game.publisher).distinct().all() if pub[0]]))
    })

# Owner-Only Admin Management Routes
@admin_bp.route('/manage-admins')
@owner_required
def manage_admins():
    """Manage all admin accounts (Owner only)"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Admin.query
    if search:
        query = query.filter(Admin.username.contains(search) | Admin.email.contains(search))
    
    admins = query.order_by(Admin.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/manage_admins.html', admins=admins, search=search)

@admin_bp.route('/manage-admins/add', methods=['GET', 'POST'])
@owner_required
def add_admin():
    """Create new admin account (Owner only)"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        if not username or not email or not password:
            flash('Username, email, and password are required!', 'error')
            return render_template('admin/admin_form.html', action='Add')
        
        # Check if admin already exists
        existing_admin = Admin.query.filter(
            (Admin.username == username) | (Admin.email == email)
        ).first()
        
        if existing_admin:
            flash('Admin with this username or email already exists!', 'error')
            return render_template('admin/admin_form.html', action='Add')
        
        try:
            new_admin = Admin()
            new_admin.username = username
            new_admin.email = email
            new_admin.full_name = full_name
            new_admin.is_active = True
            new_admin.is_owner = False  # Regular admin, not owner
            new_admin.set_password(password)
            
            db.session.add(new_admin)
            db.session.commit()
            
            flash(f'Admin "{username}" created successfully!', 'success')
            return redirect(url_for('admin.manage_admins'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating admin: {str(e)}', 'error')
    
    return render_template('admin/admin_form.html', action='Add')

@admin_bp.route('/manage-admins/toggle-status/<int:admin_id>', methods=['POST'])
@owner_required
def toggle_admin_status(admin_id):
    """Enable/disable admin account (Owner only)"""
    current_admin = get_current_admin()
    admin = Admin.query.get_or_404(admin_id)
    
    # Prevent owner from disabling themselves
    if admin.id == current_admin.id:
        flash('You cannot disable your own account!', 'error')
        return redirect(url_for('admin.manage_admins'))
    
    # Prevent disabling other owners
    if admin.is_owner:
        flash('You cannot disable another owner account!', 'error')
        return redirect(url_for('admin.manage_admins'))
    
    try:
        admin.is_active = not admin.is_active
        db.session.commit()
        
        status = "enabled" if admin.is_active else "disabled"
        flash(f'Admin "{admin.username}" has been {status}!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating admin status: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_admins'))

@admin_bp.route('/manage-admins/delete/<int:admin_id>', methods=['POST'])
@owner_required
def delete_admin(admin_id):
    """Delete admin account (Owner only)"""
    current_admin = get_current_admin()
    admin = Admin.query.get_or_404(admin_id)
    
    # Prevent owner from deleting themselves
    if admin.id == current_admin.id:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('admin.manage_admins'))
    
    # Prevent deleting other owners
    if admin.is_owner:
        flash('You cannot delete another owner account!', 'error')
        return redirect(url_for('admin.manage_admins'))
    
    try:
        # Get admin's content counts for confirmation message
        apps_count = App.query.filter_by(admin_id=admin.id).count()
        games_count = Game.query.filter_by(admin_id=admin.id).count()
        news_count = News.query.filter_by(admin_id=admin.id).count()
        
        # Delete the admin (content will be cascade deleted)
        db.session.delete(admin)
        db.session.commit()
        
        flash(f'Admin "{admin.username}" deleted successfully! '
              f'({apps_count} apps, {games_count} games, {news_count} news articles removed)', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting admin: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_admins'))

@admin_bp.route('/manage-admins/reset-password/<int:admin_id>', methods=['GET', 'POST'])
@owner_required
def reset_admin_password(admin_id):
    """Reset admin password (Owner only)"""
    admin = Admin.query.get_or_404(admin_id)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('Both password fields are required!', 'error')
            return render_template('admin/reset_password.html', admin=admin)
        
        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('admin/reset_password.html', admin=admin)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('admin/reset_password.html', admin=admin)
        
        try:
            admin.set_password(new_password)
            db.session.commit()
            
            flash(f'Password for admin "{admin.username}" has been reset successfully!', 'success')
            return redirect(url_for('admin.manage_admins'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error resetting password: {str(e)}', 'error')
    
    return render_template('admin/reset_password.html', admin=admin)