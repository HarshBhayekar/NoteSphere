from flask import Blueprint, request
from backend.middleware.auth_middleware import require_admin
from backend.services.moderation_service import ModerationService
from backend.utils.responses import success_response, error_response

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/stats", methods=["GET"])
@require_admin
def get_stats():
    """
    Admin endpoint: Returns high-level platform analytics.
    """
    stats = ModerationService.get_dashboard_stats()
    return success_response(stats, "Platform statistics retrieved successfully.")

@admin_bp.route("/notes", methods=["GET"])
@require_admin
def list_moderation_notes():
    """
    Admin endpoint: Lists submissions for moderation.
    Query param: ?status=pending|approved|rejected
    """
    status = request.args.get("status")
    if status and status not in ["pending", "approved", "rejected"]:
        return error_response("Invalid status filter. Allowed values: pending, approved, rejected.", 400)

    queue = ModerationService.list_queue(status=status)
    return success_response(queue, "Moderation queue retrieved successfully.")

@admin_bp.route("/notes/<note_id>", methods=["PATCH"])
@require_admin
def moderate_note(note_id):
    """
    Admin endpoint: Approve or reject a note.
    Expected JSON: {"status": "approved" | "rejected", "rejectionReason": "optional reason"}
    """
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    reason = data.get("rejectionReason")

    if not status:
        return error_response("Field 'status' ('approved' or 'rejected') is required.", 400)

    current_admin = request.user
    success, message = ModerationService.moderate_note(
        note_id=note_id,
        status=status,
        reviewer_uid=current_admin["uid"],
        rejection_reason=reason
    )

    if not success:
        return error_response(message, 400)

    return success_response({"noteId": note_id, "status": status}, message)

@admin_bp.route("/notes/<note_id>", methods=["DELETE"])
@require_admin
def delete_note(note_id):
    """
    Admin endpoint: Permanently removes a note and its associated Cloudinary file.
    """
    success, message = ModerationService.purge_note(note_id)
    if not success:
        return error_response(message, 400)

    return success_response({"noteId": note_id, "deleted": True}, message)
