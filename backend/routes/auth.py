from flask import Blueprint, request
from backend.middleware.auth_middleware import require_auth
from backend.services.firebase_service import FirebaseService
from backend.utils.responses import success_response, error_response

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/sync", methods=["POST"])
@require_auth
def sync_user():
    """
    Syncs the authenticated Firebase user profile with Firestore users collection.
    Enforces server-side assigned role.
    """
    current_user = request.user
    data = request.get_json(silent=True) or {}
    display_name = data.get("displayName") or current_user.get("displayName")

    synced_user = FirebaseService.sync_user(
        uid=current_user["uid"],
        email=current_user.get("email"),
        display_name=display_name
    )

    return success_response(synced_user, "User profile synchronized successfully.")

@auth_bp.route("/me", methods=["GET"])
@require_auth
def get_current_user():
    """
    Returns the currently verified user profile and role.
    """
    current_user = request.user
    # Fetch latest profile if available
    role = FirebaseService.get_user_role(current_user["uid"])
    profile = {
        **current_user,
        "role": role
    }
    return success_response(profile, "Profile retrieved successfully.")
