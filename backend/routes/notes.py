from flask import Blueprint, request, redirect, send_file
import io
from pathlib import Path
from backend.middleware.auth_middleware import require_auth, get_bearer_token
from backend.services.note_service import NoteService
from backend.services.firebase_service import FirebaseService
from backend.utils.responses import success_response, error_response
from backend.config import PROJECT_ROOT

notes_bp = Blueprint("notes", __name__, url_prefix="/api")

@notes_bp.route("/notes", methods=["GET"])
def list_notes():
    """
    Public endpoint: List approved notes with multi-facet filters.
    Query params: search, subject, semester, department, sort, limit.
    """
    search = request.args.get("search")
    subject_id = request.args.get("subject")
    semester = request.args.get("semester")
    department_id = request.args.get("department")
    sort_by = request.args.get("sort", "newest")
    limit = int(request.args.get("limit", 50))

    notes = FirebaseService.list_approved_notes(
        search=search,
        subject_id=subject_id,
        semester=semester,
        department_id=department_id,
        sort_by=sort_by,
        limit=limit
    )

    return success_response(notes, "Approved notes retrieved successfully.")

@notes_bp.route("/notes/<note_id>", methods=["GET"])
def get_note(note_id):
    """
    Public / Authenticated endpoint: Get details for a specific note.
    Only approved notes are visible publicly; pending/rejected require uploader or admin.
    """
    # Optional auth extraction
    current_user = None
    token = get_bearer_token()
    if token:
        try:
            import firebase_admin.auth
            decoded = firebase_admin.auth.verify_id_token(token)
            uid = decoded.get("uid")
            role = FirebaseService.get_user_role(uid)
            current_user = {"uid": uid, "role": role}
        except Exception:
            pass

    note, error_msg, status_code = NoteService.get_note_details(note_id, current_user)
    if error_msg:
        return error_response(error_msg, status_code)

    return success_response(note, "Note details retrieved successfully.")

@notes_bp.route("/notes", methods=["POST"])
@require_auth
def upload_note():
    """
    Protected endpoint: Upload a PDF note with metadata.
    Creates record with 'pending' moderation status.
    """
    current_user = request.user
    if "file" not in request.files:
        return error_response("PDF file is required under form field 'file'.", 400)

    pdf_file = request.files["file"]
    form_data = request.form.to_dict()

    success, errors, created_note = NoteService.upload_note(current_user, form_data, pdf_file)
    if not success:
        return error_response("Validation or upload failed.", 400, details=errors)

    return success_response(
        created_note,
        "Notes uploaded and published successfully! Your document is now live.",
        status_code=201
    )

@notes_bp.route("/notes/<note_id>", methods=["DELETE"])
@require_auth
def delete_note(note_id):
    """
    Protected endpoint: Allows students to delete their own uploaded notes.
    """
    current_user = request.user
    success, message, status_code = NoteService.delete_user_note(current_user, note_id)
    if not success:
        return error_response(message, status_code)
    return success_response({"noteId": note_id, "deleted": True}, message)

@notes_bp.route("/my-notes", methods=["GET"])
@require_auth
def my_notes():
    """
    Protected endpoint: Returns all notes uploaded by the authenticated user.
    """
    current_user = request.user
    notes = FirebaseService.list_user_notes(current_user["uid"])
    return success_response(notes, "Your uploaded notes retrieved successfully.")

@notes_bp.route("/notes/<note_id>/download", methods=["GET"])
def download_note(note_id):
    """
    Public endpoint: Checks approval, increments download count, and provides download access.
    Supports 302 redirect directly to Cloudinary or JSON response via ?json=true.
    """
    result, error_msg, status_code = NoteService.prepare_download(note_id)
    if error_msg:
        return error_response(error_msg, status_code)

    as_json = request.args.get("json", "").lower() in ["true", "1"]
    if as_json:
        return success_response(result, "Download link generated successfully.")

    # Redirect directly to Cloudinary delivery URL
    return redirect(result["downloadUrl"])

@notes_bp.route("/notes/<note_id>/mock-file", methods=["GET"])
def serve_mock_file(note_id):
    """
    Local development fallback endpoint to serve PDF from mock_uploads folder.
    """
    mock_file = PROJECT_ROOT / "backend" / "mock_uploads" / f"note_{note_id}.pdf"
    if not mock_file.exists():
        return error_response("Mock file not found.", 404)

    return send_file(
        str(mock_file),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"note_{note_id}.pdf"
    )
