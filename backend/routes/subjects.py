from flask import Blueprint, request
from backend.services.firebase_service import FirebaseService
from backend.utils.responses import success_response, error_response

subjects_bp = Blueprint("subjects", __name__, url_prefix="/api/subjects")

@subjects_bp.route("", methods=["GET"])
def list_subjects():
    """
    Public endpoint: Returns active subjects, optionally filtered by ?semester=
    """
    semester = request.args.get("semester")
    if semester:
        try:
            sem_int = int(semester)
            if sem_int < 1 or sem_int > 8:
                return error_response("Semester must be between 1 and 8.", 400)
        except ValueError:
            return error_response("Invalid semester format. Expected integer 1-8.", 400)

    subjects = FirebaseService.get_subjects(semester=semester)
    return success_response(subjects, "Subjects retrieved successfully.")
