import uuid
import logging
from backend.services.firebase_service import FirebaseService
from backend.services.cloudinary_service import CloudinaryService
from backend.utils.validators import validate_pdf_file, validate_note_metadata

logger = logging.getLogger("notesphere.note_service")

class NoteService:
    @staticmethod
    def upload_note(user, form_data, file_storage):
        """
        Coordinates full upload process: validation -> Cloudinary upload -> Firestore write.
        Executes atomic rollback of Cloudinary asset if Firestore persistence fails.
        """
        # Step 1: Validate PDF
        is_pdf_valid, pdf_err, file_bytes = validate_pdf_file(file_storage)
        if not is_pdf_valid:
            return False, {"file": pdf_err}, None

        # Step 2: Validate Metadata
        is_meta_valid, meta_errors, sanitized = validate_note_metadata(form_data)
        if not is_meta_valid:
            return False, meta_errors, None

        # Step 3: Generate Canonical Note ID
        note_id = uuid.uuid4().hex[:12]
        original_filename = file_storage.filename.strip()

        # Step 4: Upload PDF to Cloudinary
        try:
            cloudinary_meta = CloudinaryService.upload_pdf(file_bytes, note_id, original_filename)
        except Exception as e:
            logger.error("Failed to upload PDF to Cloudinary: %s", str(e))
            return False, {"upload": f"Failed to upload document to cloud storage: {str(e)}"}, None

        # Step 5: Construct Firestore Document
        note_document = {
            "title": sanitized["title"],
            "normalizedTitle": sanitized["normalizedTitle"],
            "description": sanitized["description"],
            "subjectId": sanitized["subjectId"],
            "subjectName": sanitized["subjectName"],
            "semester": sanitized["semester"],
            "departmentId": sanitized["departmentId"],
            "courseName": sanitized["courseName"],
            "tags": sanitized["tags"],
            "uploadedBy": user["uid"],
            "uploaderName": user.get("displayName") or user.get("email", "Student"),
            "originalFileName": original_filename,
            "fileFormat": "pdf",
            "mimeType": "application/pdf",
            "fileSizeBytes": len(file_bytes),
            "cloudinary": cloudinary_meta,
            "downloadUrl": cloudinary_meta.get("secureUrl"),
            "fileUrl": cloudinary_meta.get("secureUrl"),
            "status": "approved",
            "rejectionReason": None
        }

        # Step 6: Persist in Firestore with Atomic Rollback
        try:
            created_record = FirebaseService.create_note(note_id, note_document)
            logger.info("Note created and published successfully in Firestore: %s", note_id)
            return True, None, created_record
        except Exception as e:
            logger.error("Firestore persistence failed! Initiating rollback for Cloudinary asset: %s", cloudinary_meta.get("publicId"))
            try:
                CloudinaryService.delete_asset(cloudinary_meta.get("publicId"), cloudinary_meta.get("resourceType", "image"))
                logger.info("Rollback successful. Cloudinary orphan removed.")
            except Exception as rollback_err:
                logger.critical("FAILED TO ROLLBACK CLOUDINARY ASSET %s: %s", cloudinary_meta.get("publicId"), str(rollback_err))

            return False, {"database": "Failed to save note record in database. Upload has been rolled back."}, None

    @staticmethod
    def get_note_details(note_id, user=None):
        """
        Retrieves note details. All uploaded notes are publicly viewable.
        """
        note = FirebaseService.get_note_by_id(note_id)
        if not note:
            return None, "Note not found.", 404

        return note, None, 200

    @staticmethod
    def prepare_download(note_id):
        """
        Increments counter and produces authorized direct download URL for the note.
        """
        note = FirebaseService.get_note_by_id(note_id)
        if not note:
            return None, "Note not found.", 404

        # Increment download count
        FirebaseService.increment_download_count(note_id)

        # Get direct Cloudinary download URL
        cloudinary_meta = note.get("cloudinary", {})
        download_url = note.get("downloadUrl") or note.get("fileUrl") or CloudinaryService.get_download_url(cloudinary_meta, note.get("originalFileName", f"{note['title']}.pdf"))

        if not download_url:
            return None, "Download asset unavailable.", 404

        return {
            "downloadUrl": download_url,
            "filename": note.get("originalFileName", f"{note['title']}.pdf"),
            "noteId": note_id,
            "downloadCount": note.get("downloadCount", 0) + 1
        }, None, 200

    @staticmethod
    def delete_user_note(user, note_id):
        """
        Allows students to delete their own uploaded notes and purge the Cloudinary asset.
        """
        note = FirebaseService.get_note_by_id(note_id)
        if not note:
            return False, "Note not found.", 404

        if note.get("uploadedBy") != user.get("uid"):
            return False, "You can only delete notes that you uploaded.", 403

        cloudinary_meta = note.get("cloudinary", {})
        public_id = cloudinary_meta.get("publicId")
        resource_type = cloudinary_meta.get("resourceType", "image")

        if public_id:
            CloudinaryService.delete_asset(public_id, resource_type=resource_type)

        FirebaseService.delete_note(note_id)
        logger.info("User %s deleted note %s successfully.", user.get("uid"), note_id)
        return True, "Note deleted successfully.", 200
