import logging
from backend.services.firebase_service import FirebaseService
from backend.services.cloudinary_service import CloudinaryService

logger = logging.getLogger("notesphere.moderation_service")

class ModerationService:
    @staticmethod
    def get_dashboard_stats():
        """Returns statistics for the admin dashboard."""
        return FirebaseService.get_stats()

    @staticmethod
    def list_queue(status=None):
        """Returns notes filtered by moderation status."""
        return FirebaseService.list_admin_notes(status=status)

    @staticmethod
    def moderate_note(note_id, status, reviewer_uid, rejection_reason=None):
        """
        Approves or rejects a note submission.
        """
        if status not in ["approved", "rejected"]:
            return False, "Status must be either 'approved' or 'rejected'."

        if status == "rejected" and not rejection_reason:
            rejection_reason = "Submission does not meet quality or curriculum guidelines."

        note = FirebaseService.get_note_by_id(note_id)
        if not note:
            return False, "Note not found."

        success = FirebaseService.update_note_status(
            note_id=note_id,
            status=status,
            reviewer_uid=reviewer_uid,
            rejection_reason=rejection_reason
        )

        if not success:
            return False, "Failed to update note status in database."

        logger.info("Admin %s updated note %s status to '%s'", reviewer_uid, note_id, status)
        return True, f"Note successfully marked as {status}."

    @staticmethod
    def purge_note(note_id):
        """
        Permanently deletes a note document and destroys its Cloudinary asset.
        """
        note = FirebaseService.get_note_by_id(note_id)
        if not note:
            return False, "Note not found."

        cloudinary_meta = note.get("cloudinary", {})
        public_id = cloudinary_meta.get("publicId")
        resource_type = cloudinary_meta.get("resourceType", "image")

        # Step 1: Delete Cloudinary Asset
        if public_id:
            try:
                CloudinaryService.delete_asset(public_id, resource_type=resource_type)
                logger.info("Cloudinary asset %s purged successfully.", public_id)
            except Exception as e:
                logger.warning("Could not delete Cloudinary asset during purge: %s", str(e))

        # Step 2: Delete Firestore Document
        db_deleted = FirebaseService.delete_note(note_id)
        if not db_deleted:
            return False, "Asset deleted but failed to remove database record."

        logger.info("Note %s purged completely from system.", note_id)
        return True, "Note and associated file purged successfully."
