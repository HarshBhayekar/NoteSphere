import io
from backend.config import MAX_CONTENT_LENGTH, MAX_CONTENT_LENGTH_MB

PDF_MAGIC_BYTES = b"%PDF-"

def validate_pdf_file(file_storage):
    """
    Validates that the uploaded file is a genuine PDF and within size limits.
    Returns: (is_valid: bool, error_message: str or None, file_bytes: bytes or None)
    """
    if not file_storage or not file_storage.filename:
        return False, "No file was selected or uploaded.", None

    filename = file_storage.filename.strip()
    if not filename.lower().endswith(".pdf"):
        return False, "File must have a .pdf extension.", None

    # Read bytes to check signature and size
    file_bytes = file_storage.read()
    file_size = len(file_bytes)

    # Reset cursor in case caller needs to read again
    file_storage.seek(0)

    if file_size == 0:
        return False, "The uploaded PDF file is empty (0 bytes).", None

    if file_size > MAX_CONTENT_LENGTH:
        return False, f"File exceeds the maximum limit of {MAX_CONTENT_LENGTH_MB} MB.", None

    # Validate Magic Bytes / Header
    if not file_bytes.startswith(PDF_MAGIC_BYTES):
        return False, "Corrupted or invalid PDF file signature. The file is not a valid PDF document.", None

    return True, None, file_bytes

def validate_note_metadata(data):
    """
    Validates form data for note submission.
    Returns: (is_valid: bool, errors: dict or None, sanitized_data: dict)
    """
    errors = {}
    sanitized = {}

    # Title
    title = data.get("title", "").strip() if data.get("title") else ""
    if not title:
        errors["title"] = "Title is required."
    elif len(title) < 3:
        errors["title"] = "Title must be at least 3 characters."
    elif len(title) > 150:
        errors["title"] = "Title cannot exceed 150 characters."
    sanitized["title"] = title
    sanitized["normalizedTitle"] = title.lower()

    # Semester
    raw_semester = data.get("semester")
    try:
        semester = int(raw_semester)
        if semester < 1 or semester > 8:
            errors["semester"] = "Semester must be between 1 and 8."
        else:
            sanitized["semester"] = semester
    except (TypeError, ValueError):
        errors["semester"] = "A valid semester number (1-8) is required."

    # Subject
    subject_id = data.get("subjectId", "").strip() if data.get("subjectId") else ""
    subject_name = data.get("subjectName", "").strip() if data.get("subjectName") else ""
    if not subject_name and not subject_id:
        errors["subject"] = "Subject is required."
    sanitized["subjectId"] = subject_id or subject_name.lower().replace(" ", "-")
    sanitized["subjectName"] = subject_name or subject_id

    # Department
    department_id = data.get("departmentId", "").strip() if data.get("departmentId") else "computer-engineering"
    sanitized["departmentId"] = department_id
    sanitized["courseName"] = data.get("courseName", "B.Tech Computer Science / Engineering")

    # Description
    desc = data.get("description", "").strip() if data.get("description") else ""
    if len(desc) > 1000:
        errors["description"] = "Description cannot exceed 1000 characters."
    sanitized["description"] = desc

    # Tags
    raw_tags = data.get("tags", "")
    if isinstance(raw_tags, str):
        tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    elif isinstance(raw_tags, list):
        tags = [str(t).strip() for t in raw_tags if str(t).strip()]
    else:
        tags = []
    sanitized["tags"] = tags[:10]  # Max 10 tags

    if errors:
        return False, errors, sanitized
    return True, None, sanitized
