import os
import io
import logging
from pathlib import Path
import cloudinary
import cloudinary.uploader
import cloudinary.utils
from backend.config import (
    cloudinary_configured,
    CLOUDINARY_FOLDER,
    CLOUDINARY_CLOUD_NAME,
    PROJECT_ROOT
)

logger = logging.getLogger("notesphere.cloudinary_service")

# Local fallback directory when Cloudinary is not configured
MOCK_UPLOADS_DIR = PROJECT_ROOT / "backend" / "mock_uploads"
MOCK_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

class CloudinaryService:
    @staticmethod
    def is_configured():
        return cloudinary_configured

    @staticmethod
    def upload_pdf(file_bytes, note_id, filename="document.pdf"):
        """
        Uploads a PDF byte stream to Cloudinary inside the designated folder.
        Uses public_id = f"{CLOUDINARY_FOLDER}/note_{note_id}".
        Returns a dictionary with asset metadata.
        """
        public_id = f"{CLOUDINARY_FOLDER}/note_{note_id}"

        if cloudinary_configured:
            try:
                # Upload as image resource_type or raw. Cloudinary handles PDFs as 'image'
                # which enables thumbnail previews and delivery.
                response = cloudinary.uploader.upload(
                    file_bytes,
                    public_id=public_id,
                    resource_type="auto",
                    overwrite=True
                )
                res_type = response.get("resource_type", "image")
                logger.info("Cloudinary upload successful for public_id: %s (type: %s)", public_id, res_type)
                return {
                    "publicId": response.get("public_id", public_id),
                    "resourceType": response.get("resource_type", "image"),
                    "deliveryType": response.get("type", "upload"),
                    "version": response.get("version"),
                    "secureUrl": response.get("secure_url"),
                    "assetId": response.get("asset_id"),
                    "fileFormat": "pdf",
                    "fileSizeBytes": response.get("bytes", len(file_bytes))
                }
            except Exception as e:
                logger.error("Cloudinary upload failed: %s", str(e))
                raise RuntimeError(f"Cloudinary upload failed: {str(e)}")

        # Fallback local storage for mock testing
        logger.info("Cloudinary not configured; storing file locally in mock_uploads")
        mock_file_path = MOCK_UPLOADS_DIR / f"note_{note_id}.pdf"
        with open(mock_file_path, "wb") as f:
            f.write(file_bytes)

        return {
            "publicId": public_id,
            "resourceType": "mock",
            "deliveryType": "local",
            "version": 1,
            "secureUrl": f"/api/notes/{note_id}/mock-file",
            "assetId": f"mock_asset_{note_id}",
            "fileFormat": "pdf",
            "fileSizeBytes": len(file_bytes)
        }

    @staticmethod
    def delete_asset(public_id, resource_type="image"):
        """
        Deletes the file asset from Cloudinary to maintain synchronization.
        """
        if cloudinary_configured:
            try:
                res = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
                logger.info("Cloudinary deletion result for %s: %s", public_id, res)
                return res.get("result") in ["ok", "not found"]
            except Exception as e:
                logger.error("Error deleting asset %s from Cloudinary: %s", public_id, str(e))
                return False

        # Mock cleanup
        parts = public_id.split("/")
        filename = parts[-1] + ".pdf"
        mock_file = MOCK_UPLOADS_DIR / filename
        if mock_file.exists():
            mock_file.unlink()
        return True

    @staticmethod
    def get_download_url(cloudinary_meta, original_filename="notes.pdf"):
        """
        Returns the direct Cloudinary URL stored for the PDF asset.
        """
        if not cloudinary_meta:
            return None

        # Return the direct Cloudinary secure URL
        if cloudinary_meta.get("secureUrl"):
            return cloudinary_meta.get("secureUrl")

        public_id = cloudinary_meta.get("publicId")
        resource_type = cloudinary_meta.get("resourceType", "image")

        if cloudinary_configured and public_id:
            url, _ = cloudinary.utils.cloudinary_url(
                public_id,
                resource_type=resource_type,
                secure=True
            )
            return url

        return None
