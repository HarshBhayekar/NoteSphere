# FINAL TECH STACK SPECIFICATION
## Cloud-Based Notes Sharing Platform (NoteSphere)

**Project Type:** Cloud Computing Mini Project  
**Tagline:** "Your Knowledge, One Cloud Away."  
**Version:** 1.0  

---

## 1. ARCHITECTURE STACK SUMMARY

| Layer | Technology | Primary Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla ES6+) | Responsive UI, client auth flow, client-side validation, REST API consumption |
| **Backend** | Python 3, Flask REST API | API routes, business logic, authorization, input validation, cloud service coordination |
| **Authentication** | Firebase Authentication | User identity (Student & Admin), credential verification, JWT ID tokens |
| **Database** | Cloud Firestore | NoSQL document database for notes metadata, subjects, user profiles, counts |
| **File Storage** | Cloudinary | Cloud PDF storage, transformations, secure asset delivery |
| **Backend SDKs** | `firebase-admin`, `cloudinary` | Server-side Firebase verification/Firestore access and Cloudinary upload/deletion |
| **WSGI / Runtime** | Gunicorn / Python WSGI | Production-ready HTTP application server |
| **Configuration** | `python-dotenv` | Secure loading of environment variables |
| **Tooling** | VS Code, Git, GitHub | Code editing, version control, source hosting |

> [!IMPORTANT]
> **Firebase Storage is strictly NOT used in this architecture.**  
> File binaries are exclusively stored and delivered through Cloudinary.

---

## 2. PYTHON DEPENDENCIES (`requirements.txt`)

```text
Flask>=3.0.0
flask-cors>=4.0.0
firebase-admin>=6.5.0
cloudinary>=1.40.0
python-dotenv>=1.0.0
gunicorn>=22.0.0
requests>=2.31.0
```

Installation command:
```bash
pip install -r backend/requirements.txt
```

---

## 3. HOW THE END-TO-END SYSTEM WORKS

1. **Authentication:** A student or admin logs in using Firebase Authentication in the frontend. Firebase yields an ID token (JWT).
2. **API Requests:** Frontend attaches the ID token as a Bearer token in the `Authorization: Bearer <ID_TOKEN>` header for protected endpoints.
3. **Backend Verification:** Flask middleware intercepts protected requests, calls `firebase_admin.auth.verify_id_token()`, extracts user UID and checks their role against Firestore (`users/{uid}`).
4. **Note Upload:**
   - Student submits note metadata and selects a PDF file (up to 10 MB).
   - Flask validates input fields and checks file magic bytes (`%PDF-`).
   - Flask uploads the file directly to Cloudinary using the Python SDK into folder `study-notes/`.
   - Flask creates a corresponding Firestore record in `notes/{noteId}` with status `pending`.
   - If Firestore write fails, Flask rolls back by deleting the newly uploaded Cloudinary asset.
5. **Moderation:**
   - Admin accesses dashboard (`admin-dashboard.html`), viewing pending notes.
   - Admin approves or rejects (with a reason).
   - Once approved, the status is set to `approved`.
6. **Discovery & Search:**
   - Public users can search and filter only approved notes.
   - Pending/rejected notes are hidden from public queries.
7. **Secure Download:**
   - User clicks download on an approved note.
   - Flask verifies approval status, increments `downloadCount`, and generates authorized delivery access.

---

## 4. SECURITY & CREDENTIAL HANDLING

- **Server-Side Credentials:**
  - `FIREBASE_ADMIN_CREDENTIALS` (path to service account JSON or JSON content in env var).
  - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`.
  - Secret keys are loaded into `backend/config.py` via `python-dotenv`.
- **Frontend Safe Configuration:**
  - Frontend only holds public Firebase client configuration (`apiKey`, `authDomain`, `projectId`, `appId`).
  - No secret keys, service accounts, or administrative API keys in frontend JavaScript.
- **Git Safety:**
  - `.env`, service account JSON files, and virtual environments (`.venv/`) are excluded via `.gitignore`.
