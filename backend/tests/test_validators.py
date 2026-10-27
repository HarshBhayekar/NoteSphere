import unittest
import io
from werkzeug.datastructures import FileStorage
from backend.utils.validators import validate_pdf_file, validate_note_metadata
from backend.config import MAX_CONTENT_LENGTH

class TestValidators(unittest.TestCase):
    def test_valid_pdf_magic_bytes(self):
        pdf_content = b"%PDF-1.5 test content for academic note"
        file = FileStorage(
            stream=io.BytesIO(pdf_content),
            filename="unit1_notes.pdf",
            content_type="application/pdf"
        )
        is_valid, err, data = validate_pdf_file(file)
        self.assertTrue(is_valid)
        self.assertIsNone(err)
        self.assertEqual(data, pdf_content)

    def test_invalid_extension(self):
        file = FileStorage(
            stream=io.BytesIO(b"%PDF-1.4 content"),
            filename="notes.docx",
            content_type="application/octet-stream"
        )
        is_valid, err, _ = validate_pdf_file(file)
        self.assertFalse(is_valid)
        self.assertIn("must have a .pdf extension", err)

    def test_invalid_magic_bytes_spoofed_pdf(self):
        # A file with .pdf extension but plain text or malware bytes
        fake_content = b"This is not a pdf file at all"
        file = FileStorage(
            stream=io.BytesIO(fake_content),
            filename="spoofed.pdf",
            content_type="application/pdf"
        )
        is_valid, err, _ = validate_pdf_file(file)
        self.assertFalse(is_valid)
        self.assertIn("Corrupted or invalid PDF file signature", err)

    def test_empty_file(self):
        file = FileStorage(
            stream=io.BytesIO(b""),
            filename="empty.pdf",
            content_type="application/pdf"
        )
        is_valid, err, _ = validate_pdf_file(file)
        self.assertFalse(is_valid)
        self.assertIn("is empty", err)

    def test_oversized_file(self):
        # Generate stream just over max size
        large_bytes = b"%PDF-" + b"0" * (MAX_CONTENT_LENGTH + 10)
        file = FileStorage(
            stream=io.BytesIO(large_bytes),
            filename="huge.pdf",
            content_type="application/pdf"
        )
        is_valid, err, _ = validate_pdf_file(file)
        self.assertFalse(is_valid)
        self.assertIn("exceeds the maximum limit", err)

    def test_validate_metadata_success(self):
        data = {
            "title": "DBMS Unit 1 - Relational Algebra",
            "semester": "4",
            "subjectName": "Database Management Systems",
            "subjectId": "cs-sem4-dbms",
            "departmentId": "computer-engineering",
            "description": "Comprehensive notes covering relational algebra and calculus",
            "tags": "dbms, relational, sql"
        }
        is_valid, errors, sanitized = validate_note_metadata(data)
        self.assertTrue(is_valid)
        self.assertIsNone(errors)
        self.assertEqual(sanitized["semester"], 4)
        self.assertEqual(len(sanitized["tags"]), 3)
        self.assertIn("dbms", sanitized["tags"])

    def test_validate_metadata_invalid_semester(self):
        data = {
            "title": "Test Title",
            "semester": "99",
            "subjectName": "Any Subject"
        }
        is_valid, errors, _ = validate_note_metadata(data)
        self.assertFalse(is_valid)
        self.assertIn("semester", errors)

    def test_validate_metadata_missing_title(self):
        data = {
            "title": "",
            "semester": "5",
            "subjectName": "Cloud Computing"
        }
        is_valid, errors, _ = validate_note_metadata(data)
        self.assertFalse(is_valid)
        self.assertIn("title", errors)

if __name__ == "__main__":
    unittest.main()
