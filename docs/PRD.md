# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Cloud-Based Notes Sharing Platform (NoteSphere)
**Version:** 1.1  
**Status:** Ready for Development  
**Project Type:** Cloud Computing Mini Project (Semester 5)  
**Tagline:** "Your Knowledge, One Cloud Away."

---

## 1. PROJECT OVERVIEW

### 1.1 Project Description
The Cloud-Based Notes Sharing Platform (NoteSphere) is a responsive web application where students can upload, browse, search, and download academic notes and PDF study materials from anywhere with an internet connection.

The system uses:
- **Frontend:** HTML5, CSS3, and JavaScript (Vanilla)
- **Backend:** Python Flask for RESTful APIs and business logic
- **Authentication:** Firebase Authentication (Client auth + Server-side ID token verification via Firebase Admin SDK)
- **Database:** Cloud Firestore for note metadata, user roles, and academic subjects
- **File Storage & Delivery:** Cloudinary for PDF asset storage and controlled delivery
- **NOTE:** **Firebase Storage is STRICTLY NOT used** in this architecture.

### 1.2 Problem Statement
Academic materials are often scattered across messaging apps, email attachments, local devices, and disparate websites. Students struggle to find notes for specific subjects or semesters, and shared resources lack central organization, moderation, and quality control.

### 1.3 Proposed Solution
Provide a centralized platform for academic resources organized by course/department, semester, and subject. Students can submit PDF notes, search published resources, and download approved materials. Administrators moderate submissions to maintain content quality and safety.

### 1.4 Core Objectives
- Centralize academic notes and study materials.
- Enable validated PDF upload and authorized download.
- Organize notes hierarchically by department, semester, and subject.
- Provide responsive search and multi-facet filtering.
- Store PDF files on Cloudinary and document metadata in Cloud Firestore.
- Authenticate users securely via Firebase Authentication.
- Provide an admin moderation dashboard for resource lifecycle management.
- Demonstrate key Cloud Computing concepts: Cloud Auth, Cloud NoSQL DB, Cloud Asset Storage, REST APIs, and Role-Based Access Control (RBAC).

---

## 2. TARGET USERS AND ROLES

### 2.1 Student
- Browse approved notes.
- Search and filter by title, subject, semester, and department.
- View note details and download approved PDFs.
- Register and log in.
- Upload PDF notes with metadata (title, subject, semester, description, tags).
- View their own submissions and moderation status (Pending, Approved, Rejected).

### 2.2 Administrator
- Access a protected admin dashboard.
- View pending, approved, and rejected submissions.
- Approve or reject submissions with a reason.
- Remove inappropriate, duplicate, or unauthorized material (cleaning Firestore + Cloudinary).
- Manage subject and semester categories.
- View metrics (total notes, pending submissions, approved notes, rejected notes, registered users, download counts).

*Note: MVP roles are Student and Administrator only. Faculty role is out of scope for v1.1.*

---

## 3. TECHNOLOGY STACK

- **Frontend:** HTML5, CSS3, JavaScript (ES6+), FontAwesome / Feather Icons
- **Backend:** Python 3, Flask REST API, Flask-CORS
- **Authentication:** Firebase Authentication (Client SDK) + Firebase Admin SDK (Server verification)
- **Database:** Cloud Firestore
- **File Storage & CDN:** Cloudinary (Cloudinary Python SDK)
- **Environment & Utilities:** `python-dotenv`, `requests`, `gunicorn`
- **Development Tools:** VS Code, Git, GitHub, Firebase Console, Cloudinary Console

---

## 4. FUNCTIONAL REQUIREMENTS

- **FR-01 Home Page:** Branding, search bar, shortcuts by semester/subject, recent published notes, CTA for upload/login.
- **FR-02 Browse Notes:** Public listing of approved notes only. Shows title, subject, semester, upload date, file size, downloads, and download button.
- **FR-03 Search and Filters:** Search query matching title/keywords; filters by subject, semester, department; sort by newest or most downloaded.
- **FR-04 User Authentication:** Firebase Auth on frontend; Bearer ID Token sent in `Authorization` header to Flask; verified by `firebase_admin.auth.verify_id_token`.
- **FR-05 Upload Notes:** Authenticated students upload PDF + metadata. Initial status is `pending`.
- **FR-06 PDF Validation:** Enforce PDF magic bytes (`%PDF-`), limit size to 10 MB (configurable), reject malformed or non-PDF files.
- **FR-07 Cloudinary File Storage:** Store in dedicated folder (e.g. `notesphere/notes/`). Public ID stored in Firestore. Handle private/restricted delivery so unapproved notes are never exposed.
- **FR-08 Firestore Metadata:** Comprehensive metadata with server timestamps. Atomic rollback on failed database write after upload.
- **FR-09 Note Details:** Detailed view of approved notes with metadata, uploader attribution, download button, and optional PDF preview.
- **FR-10 Download Notes:** Download verification (status == `approved`), increments download count, returns secure URL or streaming response.
- **FR-11 My Uploads:** Lists user's submitted notes with status badges (`Pending`, `Approved`, `Rejected` with reason).
- **FR-12 Admin Dashboard:** Summary analytics cards and management tables.
- **FR-13 Moderation:** Admin approve/reject/delete actions with reason. Deleting a note deletes its Cloudinary asset and Firestore document.
- **FR-14 Subject and Semester Categories:** Seeded initial categories with department, semester, subject name, and subject code.
- **FR-15 Feedback and Errors:** Consistent JSON responses, clean toast/alert UI messages, no sensitive stack traces exposed.

---

## 5. NON-FUNCTIONAL REQUIREMENTS & SECURITY

- **Security:**
  - Zero trust: Backend verifies Firebase ID token and Firestore user role.
  - Server-side secrets: Service account JSON and Cloudinary API secret stored in environment variables, never committed.
  - PDF signature validation: Inspect magic bytes at byte level, not relying on client MIME type or extension.
  - Orphan prevention: Roll back Cloudinary upload if Firestore creation fails. Delete Cloudinary asset when note is deleted by admin.
- **Performance:** Paginated queries, Firestore index configurations, lightweight assets.
- **Usability:** Academic blue theme, responsive across mobile, tablet, and desktop.

---

## 6. DATA MODELS (FIRESTORE)

### Collection: `notes`
```json
{
  "title": "string",
  "description": "string",
  "subject": "string",
  "semester": 5,
  "department": "Computer Science",
  "uploadedBy": "firebase_uid",
  "uploaderName": "string",
  "cloudinaryPublicId": "notesphere/notes/xyz123",
  "cloudinaryResourceType": "image or raw",
  "fileFormat": "pdf",
  "fileSize": 2048576,
  "status": "pending | approved | rejected",
  "downloadCount": 0,
  "createdAt": "SERVER_TIMESTAMP",
  "reviewedBy": "admin_uid | null",
  "reviewedAt": "SERVER_TIMESTAMP | null",
  "rejectionReason": "string | null"
}
```

### Collection: `users`
```json
{
  "displayName": "string",
  "email": "string",
  "role": "student | admin",
  "createdAt": "SERVER_TIMESTAMP"
}
```

### Collection: `subjects`
```json
{
  "name": "Cloud Computing",
  "department": "Computer Science",
  "semester": 5,
  "subjectCode": "CS501"
}
```

---

## 7. REST API SPECIFICATION

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| `GET` | `/api/notes` | Public | List approved notes (supports `?search=&subject=&semester=&department=&sort=`) |
| `GET` | `/api/notes/<id>` | Public | Get note details (approved only unless owner/admin) |
| `POST` | `/api/notes` | Student / Admin | Upload PDF to Cloudinary + create pending note record in Firestore |
| `GET` | `/api/my-notes` | Authenticated | List submissions made by current user |
| `GET` | `/api/notes/<id>/download` | Public | Validate approved status, increment download count, return download delivery |
| `GET` | `/api/subjects` | Public | List academic subjects and categories |
| `GET` | `/api/admin/stats` | Admin | Get metrics (total, pending, approved, rejected, users, downloads) |
| `GET` | `/api/admin/notes` | Admin | List submissions for moderation (supports filter by status) |
| `PATCH` | `/api/admin/notes/<id>` | Admin | Approve or reject a note (`{ "status": "approved"|"rejected", "reason": "..." }`) |
| `DELETE` | `/api/admin/notes/<id>` | Admin | Permanently delete note and its Cloudinary asset |

---

## 8. PROJECT DIRECTORY STRUCTURE
```text
NoteSphere/
├── frontend/
│   ├── index.html
│   ├── browse.html
│   ├── note-details.html
│   ├── login.html
│   ├── register.html
│   ├── upload.html
│   ├── my-uploads.html
│   ├── admin-dashboard.html
│   ├── assets/
│   │   ├── images/
│   │   ├── icons/
│   │   └── logo.svg
│   ├── css/
│   │   ├── style.css
│   │   ├── auth.css
│   │   ├── dashboard.css
│   │   ├── upload.css
│   │   └── responsive.css
│   └── js/
│       ├── firebase-config.js
│       ├── auth.js
│       ├── api.js
│       ├── browse.js
│       ├── note-details.js
│       ├── upload.js
│       ├── my-uploads.js
│       ├── admin-dashboard.js
│       └── utils.js
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   │   ├── notes.py
│   │   ├── auth.py
│   │   ├── subjects.py
│   │   └── admin.py
│   ├── services/
│   │   ├── firebase_service.py
│   │   ├── cloudinary_service.py
│   │   ├── note_service.py
│   │   └── moderation_service.py
│   ├── middleware/
│   │   └── auth_middleware.py
│   ├── utils/
│   │   ├── validators.py
│   │   └── responses.py
│   └── tests/
├── docs/
│   ├── PRD.md
│   ├── UI_UX_Specification.md
│   ├── Database_Design.md
│   ├── System_Architecture.md
│   └── Setup_Guide.md
├── scripts/
│   └── seed_subjects.py
├── .gitignore
├── README.md
└── LICENSE
```
