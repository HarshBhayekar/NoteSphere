import unittest
import io
import json
from backend.app import create_app

class TestApiRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("storage"), "Cloudinary")

    def test_list_subjects(self):
        res = self.client.get("/api/subjects")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        subjects = data.get("data")
        self.assertIsInstance(subjects, list)
        self.assertGreater(len(subjects), 0)

    def test_list_notes_public(self):
        res = self.client.get("/api/notes")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertIsInstance(data.get("data"), list)

    def test_upload_without_token_unauthorized(self):
        res = self.client.post("/api/notes", data={})
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data.get("success"))

    def test_admin_stats_unauthorized(self):
        res = self.client.get("/api/admin/stats")
        self.assertEqual(res.status_code, 401)

    def test_admin_stats_forbidden_for_student(self):
        # Dev student token
        headers = {"Authorization": "Bearer dev-token-student-123"}
        res = self.client.get("/api/admin/stats", headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_end_to_end_upload_and_moderation_lifecycle(self):
        student_headers = {"Authorization": "Bearer dev-token-student-456"}
        admin_headers = {"Authorization": "Bearer dev-token-admin-999"}

        # 1. Student uploads a note
        pdf_content = (
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n"
            b"0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"
        )
        file_data = {
            "title": "OS Process Scheduling",
            "semester": "4",
            "subjectId": "cs-sem4-os",
            "subjectName": "Operating Systems",
            "description": "Round Robin and FCFS algorithms explained",
            "file": (io.BytesIO(pdf_content), "os_scheduling.pdf")
        }
        res_upload = self.client.post("/api/notes", data=file_data, headers=student_headers, content_type="multipart/form-data")
        self.assertEqual(res_upload.status_code, 201)
        upload_json = res_upload.get_json()
        self.assertTrue(upload_json.get("success"))
        note_id = upload_json["data"]["id"]
        self.assertEqual(upload_json["data"]["status"], "approved")

        # 2. Public query immediately shows this note
        res_public = self.client.get("/api/notes")
        public_notes = res_public.get_json()["data"]
        self.assertIn(note_id, [n["id"] for n in public_notes])

        # 3. Student checks my-notes and sees their submission
        res_my = self.client.get("/api/my-notes", headers=student_headers)
        my_notes = res_my.get_json()["data"]
        uploaded_item = next((n for n in my_notes if n["id"] == note_id), None)
        self.assertIsNotNone(uploaded_item)

        # 4. Test download request endpoint
        res_dl = self.client.get(f"/api/notes/{note_id}/download?json=true")
        self.assertEqual(res_dl.status_code, 200)
        dl_data = res_dl.get_json()
        self.assertTrue(dl_data.get("success"))
        self.assertIn("downloadUrl", dl_data["data"])

        # 5. Student deletes their own note
        res_del = self.client.delete(f"/api/notes/{note_id}", headers=student_headers)
        self.assertEqual(res_del.status_code, 200)

        # 6. Verify note is no longer in public list
        res_public_after = self.client.get("/api/notes")
        self.assertNotIn(note_id, [n["id"] for n in res_public_after.get_json()["data"]])

if __name__ == "__main__":
    unittest.main()
