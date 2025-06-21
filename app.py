import os
import json
import logging
from flask import Flask, render_template, request, url_for, redirect, abort, jsonify, make_response, send_from_directory
from flask_compress import Compress
from datetime import datetime
import markdown
from models import db, App, Game, News, Download, Comment, Reply, SearchQuery
from admin import admin_bp

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "jarmod-secret-key-2025")

# Enable GZip compression for better SEO performance
compress = Compress(app)
app.config['COMPRESS_MIMETYPES'] = [
    'text/html',
    'text/css',
    'text/xml',
    'application/json',
    'application/javascript',
    'text/javascript',
    'text/plain',
    'application/xml',
    'application/rss+xml',
    'application/atom+xml',
    'image/svg+xml'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Register blueprints
app.register_blueprint(admin_bp)

# Make admin functions available in templates
@app.context_processor
def inject_admin_context():
    from admin import get_current_admin
    return dict(get_current_admin=get_current_admin)

# Create database tables
with app.app_context():
    db.create_all()

def get_subdomain_url(slug, content_type):
    """Generate subdomain URL for app/game"""
    base_domain = os.environ.get('BASE_DOMAIN', request.host.replace('www.', ''))
    protocol = 'https' if request.is_secure else 'http'
    return f"{protocol}://{slug}.{base_domain}"

def is_subdomain_request():
    """Check if request is from a subdomain"""
    host = request.host.lower()
    
    # Skip if localhost or direct IP
    if 'localhost' in host or '127.0.0.1' in host or host.replace(':', '').replace('.', '').isdigit():
        return False
    
    # Check if it's a subdomain (not www or base domain)
    parts = host.split('.')
    if len(parts) >= 3 and parts[0] not in ['www', 'api']:
        return parts[0]  # Return subdomain
    return False

@app.before_request
def handle_subdomain_routing():
    """Handle subdomain routing and redirects"""
    subdomain = is_subdomain_request()
    
    if subdomain:
        # Request from subdomain - serve content directly
        slug = subdomain
        
        # Try to find app first, then game
        app_item = App.query.filter_by(slug=slug).first()
        if app_item:
            app_dict = app_item.to_dict()
            meta_title = app_item.meta_title if app_item.meta_title else f"Enhanced {app_dict['name']} - Premium MOD APK"
            meta_description = app_item.meta_description if app_item.meta_description else app_dict.get('short_description', app_dict.get('description', ''))[:150]
            
            return render_template('app_detail.html', 
                                 app=app_dict,
                                 meta_title=meta_title,
                                 meta_description=meta_description,
                                 canonical_url=request.url,
                                 is_subdomain=True)
        
        game_item = Game.query.filter_by(slug=slug).first()
        if game_item:
            game_dict = game_item.to_dict()
            meta_title = game_item.meta_title if game_item.meta_title else f"Play {game_dict['name']} - Modded Game APK"
            meta_description = game_item.meta_description if game_item.meta_description else game_dict.get('short_description', game_dict.get('description', ''))[:150]
            
            return render_template('game_detail.html', 
                                 game=game_dict,
                                 meta_title=meta_title,
                                 meta_description=meta_description,
                                 canonical_url=request.url,
                                 is_subdomain=True)
        
        # If no content found, redirect to main site
        base_domain = os.environ.get('BASE_DOMAIN', 'installmod.com')
        return redirect(f"https://{base_domain}", 404)

@app.before_request
def clean_request_args():
    """Remove timestamp parameters and handle old URL redirects"""
    # Skip subdomain processing (already handled above)
    if is_subdomain_request():
        return
        
    # Handle old URL structure redirects (only for app/game detail pages)
    if request.path.count('/') == 1 and len(request.path) > 1:
        slug = request.path[1:]  # Remove leading slash
        
        # Check if it's an app or game
        app_item = App.query.filter_by(slug=slug).first()
        game_item = Game.query.filter_by(slug=slug).first()
        
        if app_item or game_item:
            # Redirect to subdomain with 301 status
            subdomain_url = get_subdomain_url(slug, 'app' if app_item else 'game')
            return redirect(subdomain_url, 301)
    
    # Clean timestamp parameters
    if '_t' in request.args:
        args = request.args.to_dict()
        args.pop('_t', None)
        if args:
            return redirect(url_for(request.endpoint, **args))
        else:
            return redirect(request.path)

@app.after_request
def after_request(response):
    """Set SEO-friendly headers after each request"""
    # Enhanced robots headers for better indexing
    response.headers['X-Robots-Tag'] = 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1'
    
    # Add additional indexing hints
    response.headers['Content-Language'] = 'en'
    response.headers['Vary'] = 'Accept-Encoding, User-Agent'
    
    # Security headers that don't interfere with SEO
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Enhanced cache control for better SEO performance  
    if request.endpoint and request.endpoint.startswith('static'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year for static files
    elif request.endpoint in ['sitemap', 'robots', 'ads_txt']:
        response.headers['Cache-Control'] = 'public, max-age=86400'  # 1 day for SEO files
    elif request.endpoint in ['content_detail', 'apps_list', 'games_list', 'news_list']:
        # Allow moderate caching for content pages to help with indexing
        response.headers['Cache-Control'] = 'public, max-age=3600, must-revalidate'  # 1 hour
        response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        response.headers['Vary'] = 'Accept-Encoding, User-Agent'
    else:
        # Other dynamic content with minimal caching
        response.headers['Cache-Control'] = 'public, max-age=300, must-revalidate'  # 5 minutes
        response.headers['Vary'] = 'Accept-Encoding'
    
    return response

def get_breadcrumbs():
    """Generate breadcrumbs based on current route"""
    breadcrumbs = []
    endpoint = request.endpoint
    
    if endpoint == 'apps_list':
        breadcrumbs.append({'name': 'Apps', 'url': url_for('apps_list')})
    elif endpoint == 'games_list':
        breadcrumbs.append({'name': 'Games', 'url': url_for('games_list')})
    elif endpoint == 'news_list':
        breadcrumbs.append({'name': 'News', 'url': url_for('news_list')})
    elif endpoint == 'content_detail':
        # Handle the unified SEO-friendly content detail route
        slug = None
        if request.view_args:
            slug = request.view_args.get('slug')
        
        if slug:
            # Try to determine content type by checking each data source
            app_data = get_app_by_slug(slug)
            if app_data:
                breadcrumbs.append({'name': 'Apps', 'url': url_for('apps_list')})
                category = app_data.get('category', '').title()
                if category:
                    breadcrumbs.append({'name': category, 'url': url_for('apps_list')})
                breadcrumbs.append({'name': app_data.get('name', 'App'), 'url': None})
            else:
                game_data = get_game_by_slug(slug)
                if game_data:
                    breadcrumbs.append({'name': 'Games', 'url': url_for('games_list')})
                    category = game_data.get('category', '').title()
                    if category:
                        breadcrumbs.append({'name': category, 'url': url_for('games_list')})
                    breadcrumbs.append({'name': game_data.get('name', 'Game'), 'url': None})
                else:
                    news_data = get_news_by_slug(slug)
                    if news_data:
                        breadcrumbs.append({'name': 'News', 'url': url_for('news_list')})
                        breadcrumbs.append({'name': news_data.get('title', 'Article'), 'url': None})
    elif endpoint == 'app_detail':
        app_slug = None
        if request.view_args:
            app_slug = request.view_args.get('slug')
        app_data = get_app_by_slug(app_slug) if app_slug else None
        breadcrumbs.append({'name': 'Apps', 'url': url_for('apps_list')})
        if app_data:
            category = app_data.get('category', '').title()
            if category:
                breadcrumbs.append({'name': category, 'url': url_for('apps_list')})
            breadcrumbs.append({'name': app_data.get('name', 'App'), 'url': None})
    elif endpoint == 'game_detail':
        game_slug = None
        if request.view_args:
            game_slug = request.view_args.get('slug')
        game_data = get_game_by_slug(game_slug) if game_slug else None
        breadcrumbs.append({'name': 'Games', 'url': url_for('games_list')})
        if game_data:
            category = game_data.get('category', '').title()
            if category:
                breadcrumbs.append({'name': category, 'url': url_for('games_list')})
            breadcrumbs.append({'name': game_data.get('name', 'Game'), 'url': None})
    elif endpoint == 'news_detail':
        breadcrumbs.append({'name': 'News', 'url': url_for('news_list')})
        news_slug = None
        if request.view_args:
            news_slug = request.view_args.get('slug')
        news_data = get_news_by_slug(news_slug) if news_slug else None
        if news_data:
            breadcrumbs.append({'name': news_data.get('title', 'Article'), 'url': None})
    elif endpoint == 'search':
        query = request.args.get('q', '')
        breadcrumbs.append({'name': 'Search', 'url': '#'})
        if query:
            breadcrumbs.append({'name': f'Results for "{query}"', 'url': None})
    elif endpoint == 'publishers_list':
        breadcrumbs.append({'name': 'Publishers', 'url': url_for('publishers_list')})
    elif endpoint == 'publisher_detail':
        breadcrumbs.append({'name': 'Publishers', 'url': url_for('publishers_list')})
        if request.view_args:
            slug = request.view_args.get('slug')
            if slug:
                # Convert slug back to readable name (approximate)
                publisher_name = slug.replace('-', ' ').title()
                breadcrumbs.append({'name': publisher_name, 'url': None})
    elif endpoint == 'genres_list':
        breadcrumbs.append({'name': 'Genres', 'url': url_for('genres_list')})
    elif endpoint == 'genre_detail':
        breadcrumbs.append({'name': 'Genres', 'url': url_for('genres_list')})
        if request.view_args:
            slug = request.view_args.get('slug')
            if slug:
                # Convert slug back to readable name (approximate)
                genre_name = slug.replace('-', ' ').title()
                breadcrumbs.append({'name': genre_name, 'url': None})
    
    return breadcrumbs

# Make get_breadcrumbs available in templates
app.jinja_env.globals.update(get_breadcrumbs=get_breadcrumbs)

# Add markdown filter for templates
def markdown_filter(text):
    """Convert markdown text to HTML with heading IDs and table support"""
    if text:
        import re
        
        # Process markdown tables before standard markdown conversion
        def convert_markdown_table(text):
            # Split text into lines and process table blocks
            lines = text.split('\n')
            result_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Check if this line starts a table (contains | and has content)
                if '|' in line and line.strip() and not re.match(r'^\s*\|[\s\-\|]*\|\s*$', line):
                    # Collect all consecutive table lines
                    table_lines = [lines[i]]
                    j = i + 1
                    
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if '|' in next_line:
                            table_lines.append(lines[j])
                            j += 1
                        else:
                            break
                    
                    # Process the collected table
                    html_table = process_table_block(table_lines)
                    result_lines.append(html_table)
                    i = j
                else:
                    result_lines.append(lines[i])
                    i += 1
            
            return '\n'.join(result_lines)
        
        def process_table_block(table_lines):
            # Filter out separator lines and get content lines
            content_lines = []
            for line in table_lines:
                line = line.strip()
                if '|' in line and not re.match(r'^\s*\|[\s\-\|]*\|\s*$', line):
                    content_lines.append(line)
            
            if len(content_lines) < 2:
                return '\n'.join(table_lines)
            
            # First line is header, rest are data
            header_line = content_lines[0]
            data_lines = content_lines[1:]
            
            # Parse header - properly handle leading/trailing pipes
            header_parts = header_line.split('|')
            headers = []
            for part in header_parts:
                part = part.strip()
                if part:  # Only add non-empty parts
                    headers.append(part)
            
            if not headers:
                return '\n'.join(table_lines)
            
            # Build HTML table
            html = '<table class="table table-striped table-bordered">\n'
            html += '<thead>\n<tr>\n'
            for header in headers:
                html += f'<th>{header}</th>\n'
            html += '</tr>\n</thead>\n<tbody>\n'
            
            # Process data rows
            for line in data_lines:
                # Split by | and filter empty parts
                row_parts = line.split('|')
                cells = []
                for part in row_parts:
                    part = part.strip()
                    if part or len(cells) > 0:  # Include empty cells in middle, skip leading/trailing
                        cells.append(part)
                
                # Remove trailing empty cells
                while cells and not cells[-1]:
                    cells.pop()
                
                if len(cells) >= len(headers):
                    html += '<tr>\n'
                    for i in range(len(headers)):
                        cell = cells[i] if i < len(cells) else ''
                        # Process markdown links in cells
                        cell = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', cell)
                        html += f'<td>{cell}</td>\n'
                    html += '</tr>\n'
            
            html += '</tbody>\n</table>\n'
            return html

        
        # Process tables first, before standard markdown
        text = convert_markdown_table(text)
        
        # Convert remaining markdown to HTML
        html = markdown.markdown(text, extensions=[
            'fenced_code', 
            'codehilite',
            'nl2br',
            'attr_list'
        ], extension_configs={
            'markdown.extensions.codehilite': {'use_pygments': False}
        })
        
        # Add IDs to h2 headings for navigation
        def add_id_to_heading(match):
            heading_text = match.group(1)
            # Create slug from heading text
            slug = heading_text.lower().replace(' ', '-').replace('&', 'and')
            slug = re.sub(r'[^a-z0-9\-]', '', slug)
            return f'<h2 id="{slug}">{heading_text}</h2>'
        
        # Replace h2 tags with ID attributes
        html = re.sub(r'<h2>([^<]+)</h2>', add_id_to_heading, html)
        
        return html
    return ''

def extract_headings(text):
    """Extract h2 headings from markdown text for navigation"""
    import re
    if not text:
        return []
    
    # Find all ## headings (h2 level)
    headings = re.findall(r'^## (.+)$', text, re.MULTILINE)
    
    # Convert to navigation format
    nav_items = []
    for heading in headings:
        # Create slug from heading
        slug = heading.lower().replace(' ', '-').replace('&', 'and')
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        nav_items.append({
            'title': heading.upper(),
            'slug': slug
        })
    
    return nav_items

def publisher_to_slug(publisher_name):
    """Convert publisher name to URL slug"""
    if not publisher_name:
        return ''
    slug = publisher_name.lower().replace(' ', '-').replace('&', 'and')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    return slug

def genre_to_slug(genre_name):
    """Convert genre name to URL slug"""
    if not genre_name:
        return ''
    slug = genre_name.lower().replace(' ', '-').replace('&', 'and')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    return slug

app.jinja_env.filters['markdown'] = markdown_filter
app.jinja_env.filters['extract_headings'] = extract_headings

@app.template_filter('from_json')
def from_json_filter(value):
    """Parse JSON string to Python object"""
    if not value:
        return []
    try:
        return json.loads(value) if isinstance(value, str) else value
    except (json.JSONDecodeError, TypeError):
        return []
app.jinja_env.filters['publisher_to_slug'] = publisher_to_slug
app.jinja_env.filters['genre_to_slug'] = genre_to_slug

def get_app_by_slug(slug):
    """Get app by slug from database"""
    app = App.query.filter_by(slug=slug).first()
    return app.to_dict() if app else None

def get_game_by_slug(slug):
    """Get game by slug from database"""
    game = Game.query.filter_by(slug=slug).first()
    return game.to_dict() if game else None

def get_news_by_slug(slug):
    """Get news article by slug from database"""
    article = News.query.filter_by(slug=slug).first()
    return article.to_dict() if article else None

@app.route('/')
def index():
    """Homepage with all sections"""
    apps = [app.to_dict() for app in App.query.order_by(App.created_at.desc()).all()]
    games = [game.to_dict() for game in Game.query.order_by(Game.created_at.desc()).all()]
    news = [article.to_dict() for article in News.query.order_by(News.created_at.desc()).limit(3).all()]
    
    # Featured sections - newest first
    indispensable_apps = [app for app in apps if app.get('featured') == 'indispensable'][:6]
    editors_choice = [item for item in (games + apps) if item.get('featured') == "editors_choice"][:6]
    latest_games = games[:6]
    premium_apps = [app for app in apps if app.get('featured') == 'premium'][:6]
    
    return render_template('index.html', 
                         news=news,
                         indispensable_apps=indispensable_apps,
                         editors_choice=editors_choice,
                         latest_games=latest_games,
                         premium_apps=premium_apps)

@app.route('/news')
def news_list():
    """News listing page"""
    news = [article.to_dict() for article in News.query.order_by(News.created_at.desc()).all()]
    return render_template('news_list.html', news=news)

@app.route('/apps')
def apps_list():
    """Apps listing page"""
    apps = [app.to_dict() for app in App.query.all()]
    category = request.args.get('category')
    
    if category:
        apps = [app for app in apps if app.get('category') == category]
    
    return render_template('category.html', items=apps, category=category, type='apps')

@app.route('/games')
def games_list():
    """Games listing page"""
    games = [game.to_dict() for game in Game.query.all()]
    category = request.args.get('category')
    
    if category:
        games = [game for game in games if game.get('category') == category]
    
    return render_template('category.html', items=games, category=category, type='games')

def create_slug(text):
    """Create SEO-friendly slug from text"""
    import re
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def track_search_query(query, results_count):
    """Track search query for SEO sitemap generation"""
    if not query or len(query.strip()) < 2:
        return
    
    query_clean = query.strip()
    slug = create_slug(query_clean)
    
    try:
        # Check if query already exists (case-insensitive)
        existing_query = SearchQuery.query.filter(
            db.func.lower(SearchQuery.search_term) == query_clean.lower()
        ).first()
        
        if existing_query:
            # Update existing query
            existing_query.search_count += 1
            existing_query.last_searched = datetime.utcnow()
            existing_query.results_count = results_count
        else:
            # Create new query record with unique slug handling
            base_slug = slug
            counter = 1
            while SearchQuery.query.filter(SearchQuery.slug == slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            new_query = SearchQuery(
                search_term=query_clean,
                slug=slug,
                search_count=1,
                results_count=results_count
            )
            db.session.add(new_query)
        
        db.session.commit()
    except Exception as e:
        logging.error(f"Error tracking search query: {e}")
        db.session.rollback()

@app.route('/search')
def search():
    """Advanced search functionality with SEO tracking"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    content_type = request.args.get('type', '')
    sort_by = request.args.get('sort', 'relevance')
    
    if not query:
        return render_template('search.html', 
                             apps=[], games=[], news=[], 
                             query='', total_results=0,
                             category=category, content_type=content_type, sort_by=sort_by)
    
    query_lower = query.lower()
    apps_results = []
    games_results = []
    news_results = []
    
    # Search in apps
    if content_type in ['', 'apps']:
        apps_query = App.query
        if category:
            apps_query = apps_query.filter(App.category == category)
        
        for app in apps_query.all():
            score = 0
            app_dict = app.to_dict()
            
            # Calculate relevance score
            if query_lower in (app_dict.get('name') or '').lower():
                score += 10
            if query_lower in (app_dict.get('description') or '').lower():
                score += 5
            if query_lower in (app_dict.get('publisher') or '').lower():
                score += 3
            if app_dict.get('features'):
                try:
                    features_text = ' '.join(str(f) for f in app_dict['features']).lower()
                    if query_lower in features_text:
                        score += 2
                except (TypeError, AttributeError):
                    pass
            
            if score > 0:
                app_dict['relevance_score'] = score
                app_dict['type'] = 'app'
                apps_results.append(app_dict)
    
    # Search in games  
    if content_type in ['', 'games']:
        games_query = Game.query
        if category:
            games_query = games_query.filter(Game.category == category)
            
        for game in games_query.all():
            score = 0
            game_dict = game.to_dict()
            
            # Calculate relevance score
            if query_lower in (game_dict.get('name') or '').lower():
                score += 10
            if query_lower in (game_dict.get('description') or '').lower():
                score += 5
            if query_lower in (game_dict.get('publisher') or '').lower():
                score += 3
            if game_dict.get('features'):
                try:
                    features_text = ' '.join(str(f) for f in game_dict['features']).lower()
                    if query_lower in features_text:
                        score += 2
                except (TypeError, AttributeError):
                    pass
                
            if score > 0:
                game_dict['relevance_score'] = score
                game_dict['type'] = 'game'
                games_results.append(game_dict)
    
    # Search in news
    if content_type in ['', 'news']:
        for article in News.query.all():
            score = 0
            article_dict = article.to_dict()
            
            # Calculate relevance score
            if query_lower in (article_dict.get('title') or '').lower():
                score += 10
            if query_lower in (article_dict.get('content') or '').lower():
                score += 5
            if query_lower in (article_dict.get('excerpt') or '').lower():
                score += 3
                
            if score > 0:
                article_dict['relevance_score'] = score
                article_dict['type'] = 'news'
                news_results.append(article_dict)
    
    # Sort results
    if sort_by == 'relevance':
        apps_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        games_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        news_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    elif sort_by == 'name':
        apps_results.sort(key=lambda x: x.get('name', ''))
        games_results.sort(key=lambda x: x.get('name', ''))
        news_results.sort(key=lambda x: x.get('title', ''))
    elif sort_by == 'newest':
        apps_results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        games_results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        news_results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    total_results = len(apps_results) + len(games_results) + len(news_results)
    
    # Get categories for filters
    app_categories = [cat[0] for cat in db.session.query(App.category).distinct().all() if cat[0]]
    game_categories = [cat[0] for cat in db.session.query(Game.category).distinct().all() if cat[0]]
    all_categories = sorted(set(app_categories + game_categories))
    
    # Get search suggestions based on query
    suggestions = []
    if query and len(query) >= 2:
        # Get similar app/game names for suggestions
        all_apps = App.query.all()
        all_games = Game.query.all()
        
        for app in all_apps:
            if app.name and query_lower in app.name.lower() and app.name.lower() != query_lower:
                suggestions.append(app.name)
        
        for game in all_games:
            if game.name and query_lower in game.name.lower() and game.name.lower() != query_lower:
                suggestions.append(game.name)
        
        # Remove duplicates and limit to 5 suggestions
        suggestions = list(set(suggestions))[:5]
    
    # Track this search query for SEO sitemap generation
    track_search_query(query, total_results)
    
    return render_template('search.html', 
                         apps=apps_results, games=games_results, news=news_results,
                         query=query, total_results=total_results,
                         category=category, content_type=content_type, sort_by=sort_by,
                         categories=all_categories, suggestions=suggestions)

@app.route('/publishers')
def publishers_list():
    """Publishers listing page"""
    # Get all unique publishers from apps and games
    app_publishers = db.session.query(App.publisher).filter(App.publisher.isnot(None)).distinct().all()
    game_publishers = db.session.query(Game.publisher).filter(Game.publisher.isnot(None)).distinct().all()
    
    # Combine and deduplicate publishers
    all_publishers = set()
    for pub in app_publishers:
        if pub[0]:
            all_publishers.add(pub[0])
    for pub in game_publishers:
        if pub[0]:
            all_publishers.add(pub[0])
    
    # Create publisher data with slugs and counts
    publishers_data = []
    for publisher in sorted(all_publishers):
        slug = publisher.lower().replace(' ', '-').replace('&', 'and')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        app_count = App.query.filter_by(publisher=publisher).count()
        game_count = Game.query.filter_by(publisher=publisher).count()
        
        publishers_data.append({
            'name': publisher,
            'slug': slug,
            'app_count': app_count,
            'game_count': game_count,
            'total_count': app_count + game_count
        })
    
    return render_template('publishers.html', publishers=publishers_data)

@app.route('/publisher/<slug>')
def publisher_detail(slug):
    """Individual publisher detail page"""
    # Get all publishers to find matching one
    all_publishers = set()
    app_publishers = db.session.query(App.publisher).filter(App.publisher.isnot(None)).distinct().all()
    game_publishers = db.session.query(Game.publisher).filter(Game.publisher.isnot(None)).distinct().all()
    
    for pub in app_publishers:
        if pub[0]:
            all_publishers.add(pub[0])
    for pub in game_publishers:
        if pub[0]:
            all_publishers.add(pub[0])
    
    # Find matching publisher
    publisher_name = None
    for publisher in all_publishers:
        pub_slug = publisher.lower().replace(' ', '-').replace('&', 'and')
        pub_slug = ''.join(c for c in pub_slug if c.isalnum() or c == '-')
        if pub_slug == slug:
            publisher_name = publisher
            break
    
    if not publisher_name:
        abort(404)
    
    # Get all apps and games by this publisher
    apps = App.query.filter_by(publisher=publisher_name).all()
    games = Game.query.filter_by(publisher=publisher_name).all()
    
    # Convert to dict format for template compatibility
    apps_data = [app.to_dict() for app in apps]
    games_data = [game.to_dict() for game in games]
    
    return render_template('publisher_detail.html',
                         publisher_name=publisher_name,
                         publisher_slug=slug,
                         apps=apps_data,
                         games=games_data,
                         total_count=len(apps) + len(games))

@app.route('/genres')
def genres_list():
    """Genres listing page"""
    # Get all unique genres from apps and games
    app_genres = db.session.query(App.genre).filter(App.genre.isnot(None)).distinct().all()
    game_genres = db.session.query(Game.genre).filter(Game.genre.isnot(None)).distinct().all()
    
    # Combine and deduplicate genres
    all_genres = set()
    for genre in app_genres:
        if genre[0]:
            all_genres.add(genre[0])
    for genre in game_genres:
        if genre[0]:
            all_genres.add(genre[0])
    
    # Create genre data with slugs and counts
    genres_data = []
    for genre in sorted(all_genres):
        slug = genre.lower().replace(' ', '-').replace('&', 'and')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        app_count = App.query.filter_by(genre=genre).count()
        game_count = Game.query.filter_by(genre=genre).count()
        
        genres_data.append({
            'name': genre,
            'slug': slug,
            'app_count': app_count,
            'game_count': game_count,
            'total_count': app_count + game_count
        })
    
    return render_template('genres.html', genres=genres_data)

@app.route('/genre/<slug>')
def genre_detail(slug):
    """Individual genre detail page"""
    # Get all genres to find matching one
    all_genres = set()
    app_genres = db.session.query(App.genre).filter(App.genre.isnot(None)).distinct().all()
    game_genres = db.session.query(Game.genre).filter(Game.genre.isnot(None)).distinct().all()
    
    for genre in app_genres:
        if genre[0]:
            all_genres.add(genre[0])
    for genre in game_genres:
        if genre[0]:
            all_genres.add(genre[0])
    
    # Find matching genre
    genre_name = None
    for genre in all_genres:
        genre_slug = genre.lower().replace(' ', '-').replace('&', 'and')
        genre_slug = ''.join(c for c in genre_slug if c.isalnum() or c == '-')
        if genre_slug == slug:
            genre_name = genre
            break
    
    if not genre_name:
        abort(404)
    
    # Get all apps and games in this genre
    apps = App.query.filter_by(genre=genre_name).all()
    games = Game.query.filter_by(genre=genre_name).all()
    
    # Convert to dict format for template compatibility
    apps_data = [app.to_dict() for app in apps]
    games_data = [game.to_dict() for game in games]
    
    return render_template('genre_detail.html',
                         genre_name=genre_name,
                         genre_slug=slug,
                         apps=apps_data,
                         games=games_data,
                         total_count=len(apps) + len(games))

# Comment API routes
@app.route('/api/comments/<app_slug>')
def get_comments(app_slug):
    """Get comments for an app"""
    comments = Comment.query.filter_by(app_slug=app_slug, approved=True).order_by(Comment.date.desc()).all()
    return jsonify([comment.to_dict() for comment in comments])

@app.route('/api/comments', methods=['POST'])
def add_comment():
    """Add a new comment"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('app_slug', 'name', 'text')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    comment = Comment(
        app_slug=data['app_slug'],
        name=data['name'],
        email=data.get('email', ''),
        text=data['text']
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify(comment.to_dict()), 201

@app.route('/api/replies', methods=['POST'])
def add_reply():
    """Add a reply to a comment"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('comment_id', 'name', 'text')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if comment exists
    comment = Comment.query.get(data['comment_id'])
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    reply = Reply(
        comment_id=data['comment_id'],
        name=data['name'],
        email=data.get('email', ''),
        text=data['text']
    )
    
    db.session.add(reply)
    db.session.commit()
    
    return jsonify(reply.to_dict()), 201

# SEO-Friendly Content Routes (MUST BE LAST - catches all remaining slugs)
@app.route('/<slug>')
def content_detail(slug):
    """Handle content detail pages - apps/games redirect to subdomains, news stays here"""
    
    # Check if it's an app or game - redirect to subdomain
    app = get_app_by_slug(slug)
    if app:
        subdomain_url = get_subdomain_url(slug, 'app')
        return redirect(subdomain_url, 301)
    
    game = get_game_by_slug(slug)
    if game:
        subdomain_url = get_subdomain_url(slug, 'game')
        return redirect(subdomain_url, 301)
    
    # Handle news articles (keep original URL structure)
    article_obj = News.query.filter_by(slug=slug).first()
    if article_obj:
        # Convert markdown content to HTML with table support
        article_dict = article_obj.to_dict()
        if article_dict.get('content'):
            article_dict['content_html'] = markdown_filter(article_dict['content'])
        
        # Generate meta tags
        meta_title = article_obj.meta_title if article_obj.meta_title else article_dict['title']
        meta_description = article_obj.meta_description if article_obj.meta_description else article_dict.get('excerpt', article_dict.get('content', ''))[:150]
        
        # Get related news articles
        all_news = [news.to_dict() for news in News.query.all()]
        
        # Filter out current article and get related articles
        related_news = []
        current_category = article_dict.get('category', '').lower()
        current_id = article_dict.get('id')
        
        # First, try to find articles in the same category
        if current_category:
            category_news = [news for news in all_news 
                           if news.get('category', '').lower() == current_category 
                           and news.get('id') != current_id]
            related_news.extend(category_news[:3])
        
        # If we need more articles, add latest news (different category)
        if len(related_news) < 3:
            other_news = [news for news in all_news 
                         if news.get('id') != current_id 
                         and news not in related_news]
            # Sort by creation date (latest first)
            other_news.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            related_news.extend(other_news[:3-len(related_news)])
        
        # Pass both the model object (for datetime fields) and dict (for other data)
        return render_template('news_detail.html', 
                             article=article_obj, 
                             article_dict=article_dict,
                             related_news=related_news)
    
    # If no content found, return 404
    abort(404)

@app.route('/about')
def about():
    """About Us page"""
    return render_template('about.html')

@app.route('/advertiser')
def advertiser():
    """Advertiser page"""
    return render_template('advertiser.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/modding-required')
def modding_required():
    """Modding Required page"""
    return render_template('modding_required.html')

@app.route('/report')
def report():
    """Report page"""
    return render_template('report.html')

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml for SEO with subdomain URLs for apps/games"""
    from datetime import datetime
    
    # Get all content
    apps = [app.to_dict() for app in App.query.all()]
    games = [game.to_dict() for game in Game.query.all()]
    news = [article.to_dict() for article in News.query.all()]
    
    # Get unique publishers and genres
    publishers = list(set([app.get('publisher') for app in apps if app.get('publisher')]))
    genres = list(set([app.get('genre') for app in apps if app.get('genre')] + 
                     [game.get('genre') for game in games if game.get('genre')]))
    
    # Get all tracked search queries for SEO
    search_queries = SearchQuery.query.filter(SearchQuery.search_count >= 1).all()
    
    # Convert apps and games to use subdomain URLs
    base_domain = os.environ.get('BASE_DOMAIN', request.host.replace('www.', ''))
    protocol = 'https' if request.is_secure else 'http'
    
    for app in apps:
        app['subdomain_url'] = f"{protocol}://{app['slug']}.{base_domain}"
        
    for game in games:
        game['subdomain_url'] = f"{protocol}://{game['slug']}.{base_domain}"
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    response = make_response(render_template('sitemap_clean.xml',
                                           apps=apps,
                                           games=games,
                                           news=news,
                                           publishers=publishers,
                                           genres=genres,
                                           search_queries=search_queries,
                                           current_date=current_date,
                                           use_subdomains=True))
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/robots.txt')
def robots():
    """Generate robots.txt for SEO"""
    robots_content = f"""User-agent: *
Allow: /

# Sitemaps
Sitemap: {url_for('sitemap', _external=True)}

# Crawl delay for respectful crawling
Crawl-delay: 1

# Disallow admin and private areas
Disallow: /admin/
Disallow: /api/
Disallow: /*.json$
Disallow: /*?*utm_*
Disallow: /*?*ref=*
Disallow: /*?*fbclid=*
Disallow: /*?*gclid=*
Disallow: /*?timestamp=*

# Explicitly allow important pages and patterns
Allow: /apps$
Allow: /apps?*
Allow: /games$  
Allow: /games?*
Allow: /news$
Allow: /news?*
Allow: /search$
Allow: /search?*
Allow: /publisher/*
Allow: /genre/*
Allow: /about$
Allow: /contact$
Allow: /advertiser$
Allow: /modding-required$
Allow: /report$

# Allow all app/game detail pages
Allow: /*-mod-apk$
Allow: /*-apk$
Allow: /*-game$

User-agent: Googlebot
Allow: /
Crawl-delay: 1

User-agent: Bingbot  
Allow: /
Crawl-delay: 2
"""
    
    response = make_response(robots_content)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response

@app.route('/ads.txt')
def ads_txt():
    """Serve ads.txt file for Google AdSense verification"""
    ads_content = "google.com, pub-4858972826245644, DIRECT, f08c47fec0942fa0"
    
    response = make_response(ads_content)
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/site.webmanifest')
def web_manifest():
    """Serve web app manifest file"""
    return send_from_directory('static/images', 'site.webmanifest', mimetype='application/manifest+json')

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('base.html', error="Page not found"), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
