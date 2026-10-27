import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("notesphere.config")

# Resolve project directories
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
ENV_PATH = PROJECT_ROOT / ".env"
BACKEND_ENV_PATH = BACKEND_DIR / ".env"

# Load environment variables
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
elif BACKEND_ENV_PATH.exists():
    load_dotenv(dotenv_path=BACKEND_ENV_PATH)
else:
    load_dotenv()

# App Settings
FLASK_ENV = os.getenv("FLASK_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-notesphere-cc-project-2026")
PORT = int(os.getenv("PORT", 5000))

# 10 MB default limit (in bytes)
MAX_CONTENT_LENGTH_MB = int(os.getenv("MAX_CONTENT_LENGTH_MB", 10))
MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH_MB * 1024 * 1024

# Admin email bootstrap
raw_admin_emails = os.getenv("ADMIN_EMAILS", "admin@notesphere.edu,admin@example.com")
ADMIN_EMAILS = [email.strip().lower() for email in raw_admin_emails.split(",") if email.strip()]

# Cloudinary Setup
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "study-notes")

import cloudinary

cloudinary_configured = False
if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True
    )
    cloudinary_configured = True
    logger.info("Cloudinary configured successfully for cloud: %s", CLOUDINARY_CLOUD_NAME)
else:
    logger.warning("Cloudinary credentials missing or incomplete. Real file upload requires CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET in .env")

# Firebase Admin SDK & Firestore Setup
import json
import firebase_admin
from firebase_admin import credentials, firestore

firebase_app = None
firestore_db = None
firebase_configured = False

cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "backend/serviceAccountKey.json")
resolved_cred_path = (PROJECT_ROOT / cred_path) if not Path(cred_path).is_absolute() else Path(cred_path)
firebase_json_env = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

try:
    if firebase_json_env:
        try:
            cred_dict = json.loads(firebase_json_env)
            cred = credentials.Certificate(cred_dict)
            firebase_app = firebase_admin.initialize_app(cred)
            firestore_db = firestore.client()
            firebase_configured = True
            logger.info("Firebase Admin initialized from FIREBASE_SERVICE_ACCOUNT_JSON env var")
        except Exception as json_err:
            logger.error("Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON: %s", str(json_err))

    if not firebase_configured:
        if resolved_cred_path.exists():
            cred = credentials.Certificate(str(resolved_cred_path))
            firebase_app = firebase_admin.initialize_app(cred)
            firestore_db = firestore.client()
            firebase_configured = True
            logger.info("Firebase Admin initialized with service account at: %s", resolved_cred_path)
        elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            firebase_app = firebase_admin.initialize_app()
            firestore_db = firestore.client()
            firebase_configured = True
            logger.info("Firebase Admin initialized via GOOGLE_APPLICATION_CREDENTIALS")
        else:
            logger.warning(
                "Firebase credentials file not found at %s. Running in development mode without live Firebase.",
                resolved_cred_path
            )
except Exception as e:
    logger.error("Error initializing Firebase Admin SDK: %s", str(e))

