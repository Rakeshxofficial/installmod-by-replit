from app import app

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
