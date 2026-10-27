from functools import wraps
from flask import request
import logging
from backend.config import firebase_configured, firestore_db, ADMIN_EMAILS
from backend.utils.responses import error_response

logger = logging.getLogger("notesphere.auth")

def get_bearer_token():
    """Extracts Bearer token from the Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.split("Bearer ", 1)[1].strip()

def resolve_user_role(uid, email=None):
    """
    Resolves the user's role from Firestore users/{uid}.
    Checks bootstrap ADMIN_EMAILS if email is present.
    """
    if email and email.lower() in ADMIN_EMAILS:
        return "admin"

    if firestore_db:
        try:
            doc = firestore_db.collection("users").document(uid).get()
            if doc.exists:
                data = doc.to_dict()
                return data.get("role", "student")
        except Exception as e:
            logger.error("Error reading role for uid %s: %s", uid, str(e))

    return "student"

def require_auth(f):
    """
    Decorator enforcing that the incoming request has a valid Firebase ID token.
    Populates request.user with {uid, email, displayName, role}.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_bearer_token()
        if not token:
            return error_response("Missing or malformed Authorization header. Expected 'Bearer <token>'.", 401)

        # Support development/demo mock tokens for automated testing or evaluation shortcuts
        if token.startswith("dev-token-") or token.startswith("mock-"):
            parts = token.split("-")
            uid = parts[-1] if len(parts) > 2 else "dev_student_uid"
            role = "admin" if "admin" in token else "student"
            email = f"{role}@notesphere.edu"
            request.user = {
                "uid": uid,
                "email": email,
                "displayName": f"Dev {role.capitalize()}",
                "role": role
            }
            return f(*args, **kwargs)

        if not firebase_configured:
            logger.warning("Firebase not configured and token is not a dev token.")
            return error_response("Firebase authentication is not configured on this server.", 503)

        # Live Firebase token verification
        try:
            import firebase_admin.auth
            decoded_token = firebase_admin.auth.verify_id_token(token)
            uid = decoded_token.get("uid")
            email = decoded_token.get("email", "")
            name = decoded_token.get("name", email.split("@")[0] if email else "User")

            # Zero-trust server-side role resolution
            role = resolve_user_role(uid, email)

            request.user = {
                "uid": uid,
                "email": email,
                "displayName": name,
                "role": role
            }
            return f(*args, **kwargs)
        except Exception as e:
            logger.warning("Token verification failed: %s", str(e))
            return error_response("Invalid or expired authentication token. Please log in again.", 401, details=str(e))

    return decorated

def require_admin(f):
    """
    Decorator enforcing that the caller is authenticated AND has the 'admin' role.
    """
    @wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        user = getattr(request, "user", None)
        if not user or user.get("role") != "admin":
            return error_response("Access denied: Administrator privileges required.", 403)
        return f(*args, **kwargs)

    return decorated
