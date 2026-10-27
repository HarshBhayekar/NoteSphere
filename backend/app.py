import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from backend.config import (
    SECRET_KEY,
    MAX_CONTENT_LENGTH,
    PORT
)
from backend.routes.auth import auth_bp
from backend.routes.subjects import subjects_bp
from backend.routes.notes import notes_bp
from backend.routes.admin import admin_bp
from backend.utils.responses import error_response

FRONTEND_DIR = PROJECT_ROOT / "public"
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = PROJECT_ROOT / "frontend"

def create_app():
    """Application factory for NoteSphere Flask Backend."""
    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    # Enable CORS for all API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(admin_bp)

    # API Root endpoint
    @app.route("/api", methods=["GET"])
    @app.route("/api/", methods=["GET"])
    def api_root():
        return jsonify({
            "status": "healthy",
            "service": "NoteSphere Backend API",
            "version": "1.1",
            "endpoints": {
                "health": "/api/health",
                "notes": "/api/notes",
                "subjects": "/api/subjects"
            }
        }), 200

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "NoteSphere Backend API",
            "version": "1.1",
            "storage": "Cloudinary",
            "database": "Cloud Firestore",
            "auth": "Firebase Authentication"
        }), 200

    # Serve Frontend UI
    @app.route("/")
    def serve_index():
        if (FRONTEND_DIR / "index.html").exists():
            return send_from_directory(str(FRONTEND_DIR), "index.html")
        return jsonify({"service": "NoteSphere Backend", "status": "running"}), 200

    @app.route("/<path:path>")
    def serve_frontend_files(path):
        target = FRONTEND_DIR / path
        if target.exists() and not target.is_dir():
            return send_from_directory(str(FRONTEND_DIR), path)
        # Check if path.html exists
        html_target = FRONTEND_DIR / f"{path}.html"
        if html_target.exists():
            return send_from_directory(str(FRONTEND_DIR), f"{path}.html")
        # Default fallback to index.html if present
        if (FRONTEND_DIR / "index.html").exists():
            return send_from_directory(str(FRONTEND_DIR), "index.html")
        return error_response("The requested resource or endpoint was not found.", 404)

    # Global Error Handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return error_response("Uploaded file exceeds the maximum allowed limit of 10 MB.", 413)

    @app.errorhandler(404)
    def not_found_handler(error):
        return error_response("The requested resource or endpoint was not found.", 404)

    @app.errorhandler(500)
    def internal_server_error(error):
        return error_response("An internal server error occurred. Please try again later.", 500)

    return app

app = create_app()

if __name__ == "__main__":
    print(f"Starting NoteSphere Backend on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
