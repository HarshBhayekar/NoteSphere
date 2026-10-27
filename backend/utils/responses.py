from flask import jsonify

def success_response(data=None, message="Operation successful", status_code=200):
    """Generates a standardized JSON success response."""
    payload = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(payload), status_code

def error_response(message="An error occurred", status_code=400, details=None):
    """Generates a standardized JSON error response."""
    payload = {
        "success": False,
        "message": message
    }
    if details is not None:
        payload["error"] = details
    return jsonify(payload), status_code
