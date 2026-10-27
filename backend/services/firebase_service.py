import logging
import uuid
from datetime import datetime, timezone
from backend.config import firestore_db, firebase_configured, ADMIN_EMAILS
import firebase_admin.firestore as f_store

logger = logging.getLogger("notesphere.firebase_service")

try:
    from google.cloud.firestore_v1.base_query import FieldFilter
except ImportError:
    FieldFilter = None

def _apply_filter(query, field, op, val):
    if FieldFilter:
        return query.where(filter=FieldFilter(field, op, val))
    return query.where(field, op, val)

# In-memory storage fallback for local development/testing before live Firestore is linked
_local_notes = {}
_local_users = {}
_local_subjects = [
    {"id": "cs-sem1-math1", "name": "Engineering Mathematics I", "normalizedName": "engineering mathematics i", "subjectCode": "MATH101", "departmentId": "computer-engineering", "semester": 1, "isActive": True},
    {"id": "cs-sem1-phy", "name": "Engineering Physics", "normalizedName": "engineering physics", "subjectCode": "PHY101", "departmentId": "computer-engineering", "semester": 1, "isActive": True},
    {"id": "cs-sem2-cprog", "name": "Programming in C", "normalizedName": "programming in c", "subjectCode": "CS102", "departmentId": "computer-engineering", "semester": 2, "isActive": True},
    {"id": "cs-sem3-dsa", "name": "Data Structures & Algorithms", "normalizedName": "data structures & algorithms", "subjectCode": "CS301", "departmentId": "computer-engineering", "semester": 3, "isActive": True},
    {"id": "cs-sem3-co", "name": "Computer Organization", "normalizedName": "computer organization", "subjectCode": "CS302", "departmentId": "computer-engineering", "semester": 3, "isActive": True},
    {"id": "cs-sem4-dbms", "name": "Database Management Systems", "normalizedName": "database management systems", "subjectCode": "CS401", "departmentId": "computer-engineering", "semester": 4, "isActive": True},
    {"id": "cs-sem4-os", "name": "Operating Systems", "normalizedName": "operating systems", "subjectCode": "CS402", "departmentId": "computer-engineering", "semester": 4, "isActive": True},
    {"id": "cs-sem5-cn", "name": "Computer Networks", "normalizedName": "computer networks", "subjectCode": "CS501", "departmentId": "computer-engineering", "semester": 5, "isActive": True},
    {"id": "cs-sem5-cc", "name": "Cloud Computing", "normalizedName": "cloud computing", "subjectCode": "CS502", "departmentId": "computer-engineering", "semester": 5, "isActive": True},
    {"id": "cs-sem6-se", "name": "Software Engineering", "normalizedName": "software engineering", "subjectCode": "CS601", "departmentId": "computer-engineering", "semester": 6, "isActive": True},
    {"id": "cs-sem6-ai", "name": "Artificial Intelligence", "normalizedName": "artificial intelligence", "subjectCode": "CS602", "departmentId": "computer-engineering", "semester": 6, "isActive": True},
    {"id": "cs-sem7-ml", "name": "Machine Learning", "normalizedName": "machine learning", "subjectCode": "CS701", "departmentId": "computer-engineering", "semester": 7, "isActive": True},
    {"id": "cs-sem8-cns", "name": "Cyber & Information Security", "normalizedName": "cyber & information security", "subjectCode": "CS801", "departmentId": "computer-engineering", "semester": 8, "isActive": True},
]

class FirebaseService:
    @staticmethod
    def is_live():
        return firestore_db is not None

    # ==================== USERS ====================
    @staticmethod
    def sync_user(uid, email, display_name=None, requested_role=None):
        """Creates or updates a user profile. Enforces server-side role assignment."""
        now = datetime.now(timezone.utc).isoformat()
        assigned_role = "admin" if (email and email.lower() in ADMIN_EMAILS) else "student"

        if firestore_db:
            try:
                import firebase_admin.firestore as f_store
                user_ref = firestore_db.collection("users").document(uid)
                doc = user_ref.get()
                if doc.exists:
                    d = doc.to_dict()
                    current_role = d.get("role", assigned_role)
                    user_ref.update({
                        "displayName": display_name or d.get("displayName", ""),
                        "email": email or d.get("email", ""),
                        "updatedAt": f_store.SERVER_TIMESTAMP
                    })
                    for k in ["createdAt", "updatedAt", "lastLoginAt"]:
                        if d.get(k) and hasattr(d[k], "isoformat"):
                            d[k] = d[k].isoformat()
                        elif d.get(k) and not isinstance(d[k], (str, int, float, bool)):
                            d[k] = now
                    d["role"] = current_role
                    if display_name:
                        d["displayName"] = display_name
                    return d
                else:
                    new_user = {
                        "uid": uid,
                        "displayName": display_name or (email.split("@")[0] if email else "Student"),
                        "email": email,
                        "role": assigned_role,
                        "departmentId": "computer-engineering",
                        "createdAt": f_store.SERVER_TIMESTAMP,
                        "updatedAt": f_store.SERVER_TIMESTAMP,
                        "isActive": True
                    }
                    user_ref.set(new_user)
                    return {
                        **new_user,
                        "createdAt": now,
                        "updatedAt": now
                    }
            except Exception as e:
                logger.error("Error syncing user in Firestore: %s", str(e))

        # Local fallback
        if uid in _local_users:
            _local_users[uid]["updatedAt"] = now
            if display_name:
                _local_users[uid]["displayName"] = display_name
            return _local_users[uid]
        else:
            user_data = {
                "uid": uid,
                "displayName": display_name or (email.split("@")[0] if email else "Student"),
                "email": email,
                "role": assigned_role,
                "departmentId": "computer-engineering",
                "createdAt": now,
                "updatedAt": now,
                "isActive": True
            }
            _local_users[uid] = user_data
            return user_data

    @staticmethod
    def get_user_role(uid):
        if firestore_db:
            try:
                doc = firestore_db.collection("users").document(uid).get()
                if doc.exists:
                    return doc.to_dict().get("role", "student")
            except Exception as e:
                logger.error("Error reading user role: %s", str(e))
        return _local_users.get(uid, {}).get("role", "student")

    # ==================== SUBJECTS ====================
    @staticmethod
    def get_subjects(semester=None):
        """Returns active subjects, optionally filtered by semester."""
        if firestore_db:
            try:
                query = _apply_filter(firestore_db.collection("subjects"), "isActive", "==", True)
                if semester:
                    query = _apply_filter(query, "semester", "==", int(semester))
                docs = query.stream()
                subjects = []
                for doc in docs:
                    d = doc.to_dict()
                    d["id"] = doc.id
                    subjects.append(d)
                if subjects:
                    return subjects
            except Exception as e:
                logger.error("Error reading subjects from Firestore: %s", str(e))

        # Fallback seeded subjects
        results = _local_subjects
        if semester:
            results = [s for s in results if s.get("semester") == int(semester)]
        return results

    # ==================== NOTES ====================
    @staticmethod
    def create_note(note_id, note_data):
        """Writes note document to Firestore with status 'pending'."""
        now = datetime.now(timezone.utc).isoformat()
        if firestore_db:
            import firebase_admin.firestore as f_store
            firestore_data = {
                **note_data,
                "createdAt": f_store.SERVER_TIMESTAMP,
                "updatedAt": f_store.SERVER_TIMESTAMP,
                "reviewedAt": None,
                "reviewedBy": None,
                "approvedAt": None,
                "downloadCount": 0
            }
            firestore_db.collection("notes").document(note_id).set(firestore_data)
            return {**note_data, "id": note_id, "createdAt": now, "downloadCount": 0}

        # Fallback
        record = {
            **note_data,
            "id": note_id,
            "createdAt": now,
            "updatedAt": now,
            "reviewedAt": None,
            "reviewedBy": None,
            "approvedAt": None,
            "downloadCount": 0
        }
        _local_notes[note_id] = record
        return record

    @staticmethod
    def get_note_by_id(note_id):
        """Fetches a single note by its document ID."""
        if firestore_db:
            try:
                doc = firestore_db.collection("notes").document(note_id).get()
                if doc.exists:
                    d = doc.to_dict()
                    d["id"] = doc.id
                    # Convert Firestore timestamps to ISO string if necessary
                    for k in ["createdAt", "updatedAt", "reviewedAt", "approvedAt"]:
                        if d.get(k) and hasattr(d[k], "isoformat"):
                            d[k] = d[k].isoformat()
                    return d
                return None
            except Exception as e:
                logger.error("Error getting note %s from Firestore: %s", note_id, str(e))

        return _local_notes.get(note_id)

    @staticmethod
    def list_approved_notes(search=None, subject_id=None, semester=None, department_id=None, sort_by="newest", limit=50):
        """Queries approved notes for public browsing."""
        notes = []
        if firestore_db:
            try:
                query = _apply_filter(firestore_db.collection("notes"), "status", "==", "approved")
                if subject_id:
                    query = _apply_filter(query, "subjectId", "==", subject_id)
                if semester:
                    query = _apply_filter(query, "semester", "==", int(semester))
                if department_id:
                    query = _apply_filter(query, "departmentId", "==", department_id)

                try:
                    if sort_by == "downloads":
                        ordered_query = query.order_by("downloadCount", direction=f_store.Query.DESCENDING)
                    else:
                        ordered_query = query.order_by("createdAt", direction=f_store.Query.DESCENDING)
                    stream_docs = list(ordered_query.limit(limit).stream())
                except Exception:
                    # Fallback if composite index is not yet built in Firestore
                    stream_docs = list(query.limit(limit).stream())

                for doc in stream_docs:
                    d = doc.to_dict()
                    d["id"] = doc.id
                    for k in ["createdAt", "updatedAt", "reviewedAt", "approvedAt"]:
                        if d.get(k) and hasattr(d[k], "isoformat"):
                            d[k] = d[k].isoformat()
                    notes.append(d)
            except Exception as e:
                logger.error("Error querying approved notes: %s", str(e))
                notes = [n for n in _local_notes.values() if n.get("status") == "approved"]
        else:
            notes = [n for n in _local_notes.values() if n.get("status") == "approved"]

        # Apply client/search filtering if requested
        if semester and not firestore_db:
            notes = [n for n in notes if n.get("semester") == int(semester)]
        if subject_id and not firestore_db:
            notes = [n for n in notes if n.get("subjectId") == subject_id]
        if search:
            q = search.lower().strip()
            notes = [
                n for n in notes
                if q in n.get("normalizedTitle", "")
                or q in n.get("subjectName", "").lower()
                or any(q in t.lower() for t in n.get("tags", []))
            ]

        if sort_by == "downloads":
            notes.sort(key=lambda x: x.get("downloadCount", 0), reverse=True)
        else:
            notes.sort(key=lambda x: str(x.get("createdAt", "")), reverse=True)

        return notes[:limit]

    @staticmethod
    def list_user_notes(uid):
        """Returns all notes uploaded by a specific user."""
        notes = []
        if firestore_db:
            try:
                query = _apply_filter(firestore_db.collection("notes"), "uploadedBy", "==", uid)
                try:
                    ordered_query = query.order_by("createdAt", direction=f_store.Query.DESCENDING)
                    stream_docs = list(ordered_query.stream())
                except Exception:
                    # Fallback if composite index is not yet built
                    stream_docs = list(query.stream())

                for doc in stream_docs:
                    d = doc.to_dict()
                    d["id"] = doc.id
                    for k in ["createdAt", "updatedAt", "reviewedAt", "approvedAt"]:
                        if d.get(k) and hasattr(d[k], "isoformat"):
                            d[k] = d[k].isoformat()
                    notes.append(d)
                notes.sort(key=lambda x: str(x.get("createdAt", "")), reverse=True)
                return notes
            except Exception as e:
                logger.error("Error reading user notes for %s: %s", uid, str(e))

        user_notes = [n for n in _local_notes.values() if n.get("uploadedBy") == uid]
        user_notes.sort(key=lambda x: str(x.get("createdAt", "")), reverse=True)
        return user_notes

    @staticmethod
    def list_admin_notes(status=None):
        """Admin listing of notes by status (pending, approved, rejected)."""
        notes = []
        if firestore_db:
            try:
                import firebase_admin.firestore as f_store
                query = firestore_db.collection("notes")
                if status:
                    query = _apply_filter(query, "status", "==", status)
                docs = query.stream()
                for doc in docs:
                    d = doc.to_dict()
                    d["id"] = doc.id
                    for k in ["createdAt", "updatedAt", "reviewedAt", "approvedAt"]:
                        if d.get(k) and hasattr(d[k], "isoformat"):
                            d[k] = d[k].isoformat()
                    notes.append(d)
                notes.sort(key=lambda x: str(x.get("createdAt", "")), reverse=True)
                return notes
            except Exception as e:
                logger.error("Error reading admin notes: %s", str(e))

        admin_notes = list(_local_notes.values())
        if status:
            admin_notes = [n for n in admin_notes if n.get("status") == status]
        admin_notes.sort(key=lambda x: str(x.get("createdAt", "")), reverse=True)
        return admin_notes

    @staticmethod
    def update_note_status(note_id, status, reviewer_uid=None, rejection_reason=None):
        """Transitions note status (approved/rejected)."""
        now = datetime.now(timezone.utc).isoformat()
        updates = {
            "status": status,
            "reviewedBy": reviewer_uid,
            "rejectionReason": rejection_reason if status == "rejected" else None
        }
        if status == "approved":
            updates["approvedAt"] = now

        if firestore_db:
            try:
                import firebase_admin.firestore as f_store
                fs_updates = {
                    "status": status,
                    "reviewedBy": reviewer_uid,
                    "reviewedAt": f_store.SERVER_TIMESTAMP,
                    "updatedAt": f_store.SERVER_TIMESTAMP,
                    "rejectionReason": rejection_reason if status == "rejected" else None
                }
                if status == "approved":
                    fs_updates["approvedAt"] = f_store.SERVER_TIMESTAMP
                firestore_db.collection("notes").document(note_id).update(fs_updates)
                return True
            except Exception as e:
                logger.error("Error updating note status in Firestore: %s", str(e))
                return False

        if note_id in _local_notes:
            _local_notes[note_id].update(updates)
            _local_notes[note_id]["reviewedAt"] = now
            _local_notes[note_id]["updatedAt"] = now
            return True
        return False

    @staticmethod
    def increment_download_count(note_id):
        """Increments the note's download counter atomically."""
        if firestore_db:
            try:
                import firebase_admin.firestore as f_store
                firestore_db.collection("notes").document(note_id).update({
                    "downloadCount": f_store.Increment(1)
                })
                return True
            except Exception as e:
                logger.error("Error incrementing download count: %s", str(e))

        if note_id in _local_notes:
            _local_notes[note_id]["downloadCount"] = _local_notes[note_id].get("downloadCount", 0) + 1
            return True
        return False

    @staticmethod
    def delete_note(note_id):
        """Removes note document from Firestore."""
        if firestore_db:
            try:
                firestore_db.collection("notes").document(note_id).delete()
                return True
            except Exception as e:
                logger.error("Error deleting note from Firestore: %s", str(e))
                return False

        if note_id in _local_notes:
            del _local_notes[note_id]
            return True
        return False

    @staticmethod
    def get_stats():
        """Aggregates metrics for the admin dashboard."""
        all_notes = []
        user_count = 0

        if firestore_db:
            try:
                for doc in firestore_db.collection("notes").stream():
                    all_notes.append(doc.to_dict())
                users_stream = firestore_db.collection("users").stream()
                user_count = sum(1 for _ in users_stream)
            except Exception as e:
                logger.error("Error fetching admin stats from Firestore: %s", str(e))
                all_notes = list(_local_notes.values())
                user_count = len(_local_users)
        else:
            all_notes = list(_local_notes.values())
            user_count = len(_local_users)

        total_notes = len(all_notes)
        pending = sum(1 for n in all_notes if n.get("status") == "pending")
        approved = sum(1 for n in all_notes if n.get("status") == "approved")
        rejected = sum(1 for n in all_notes if n.get("status") == "rejected")
        total_downloads = sum(n.get("downloadCount", 0) for n in all_notes)

        return {
            "totalNotes": total_notes,
            "pendingNotes": pending,
            "approvedNotes": approved,
            "rejectedNotes": rejected,
            "totalDownloads": total_downloads,
            "registeredUsers": max(user_count, 1)
        }
