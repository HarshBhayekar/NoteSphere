# NoteSphere: Cloud-Based Notes Sharing Platform

> *"Your Knowledge, One Cloud Away."*  
> **Course:** Cloud Computing Mini Project (Semester 5)  
> **Architecture:** Python Flask + Vanilla HTML5/CSS3/JavaScript + Firebase Auth + Cloud Firestore + Cloudinary

---

## 1. Overview & Cloud Architecture

**NoteSphere** is a centralized, cloud-native web platform designed for college engineering students to upload, discover, search, and download verified academic notes and PDF materials.

```text
[ Client Web App ]
(HTML5, CSS3, Vanilla JS)
        |
        | 1. Authenticate (Firebase Client SDK)
        v
[ Firebase Authentication ] ---> Returns JWT ID Token
        |
        | 2. API Request with Bearer ID Token
        v
[ Python Flask Backend ]
        |
        +---> [ Firebase Admin SDK ]
        |        |-- Verifies JWT ID Token
        |        \-- Reads / Writes Cloud Firestore (Metadata, Users, Subjects)
        |
        \---> [ Cloudinary Python SDK ]
                 |-- Uploads & stores PDF documents (Folder: study-notes/)
                 |-- Generates secure download & attachment URLs
                 \-- Destroys assets on rollback or admin deletion
```

### Key Architectural Constraint:
* **Cloudinary** is the exclusive cloud storage & delivery service for PDF binaries.
* **Cloud Firestore** is the exclusive database for metadata, subject taxonomy, and Cloudinary references.
* **Firebase Authentication** manages user identity.
* **Firebase Storage is STRICTLY NOT USED** in this architecture.

---

## 2. Technology Stack

* **Frontend:** Vanilla HTML5, CSS3, ES6+ JavaScript, Inter Typography
* **Backend:** Python 3.10+, Flask 3.0+, Flask-CORS, Gunicorn
* **Cloud Authentication:** Firebase Authentication + Firebase Admin SDK
* **Cloud Database:** Cloud Firestore (NoSQL Document Store)
* **Cloud File Storage:** Cloudinary + Cloudinary Python SDK
* **Testing:** Python `unittest` suite (15 automated unit & integration tests)

---

## 3. Project Directory Structure

```text
NoteSphere/
├── frontend/
│   ├── index.html              # Home page with hero, search, semester shortcuts
│   ├── browse.html             # Multi-filter notes catalog with live search
│   ├── note-details.html       # Note details & secure Cloudinary download
│   ├── upload.html             # PDF drag-and-drop upload form
│   ├── my-uploads.html         # User's submissions tracking & status badges
│   ├── login.html              # Sign in card with 1-click demo shortcuts
│   ├── register.html           # Account registration
│   ├── admin-dashboard.html    # Admin metrics & moderation queue
│   ├── assets/
│   │   └── logo.svg            # NoteSphere brand logo
│   ├── css/
│   │   ├── style.css           # Core design system tokens & base UI
│   │   ├── auth.css            # Centered authentication cards
│   │   ├── upload.css          # Drag-and-drop PDF dropzone styles
│   │   ├── dashboard.css       # Analytics cards & data tables
│   │   └── responsive.css      # Desktop, tablet, mobile media queries
│   └── js/
│       ├── firebase-config.js  # Firebase client credentials
│       ├── utils.js            # Toasts, modals, date/filesize formatters
│       ├── api.js              # Central HTTP client with Bearer tokens
│       ├── auth.js             # Sign-in, sign-up, sign-out & session state
│       ├── browse.js           # Catalog search, filter, and card renderer
│       ├── upload.js           # PDF validation & submission workflow
│       ├── note-details.js     # Single note details fetcher
│       ├── my-uploads.js       # Student submission monitor
│       └── admin-dashboard.js  # Admin stats & moderation actions
├── backend/
│   ├── app.py                  # Flask app factory, static server, routes
│   ├── config.py               # Environment configuration & SDK setup
│   ├── requirements.txt        # Python backend dependencies
│   ├── .env.example            # Environment variables template
│   ├── middleware/
│   │   └── auth_middleware.py  # Zero-trust Firebase ID token & RBAC checks
│   ├── utils/
│   │   ├── validators.py       # PDF %PDF- magic bytes & form validation
│   │   └── responses.py        # Standardized JSON response formatters
│   ├── services/
│   │   ├── firebase_service.py # Firestore CRUD & local dev fallback
│   │   ├── cloudinary_service.py # Cloudinary PDF upload, purge & download
│   │   ├── note_service.py     # Upload atomicity, details, download logic
│   │   └── moderation_service.py # Dashboard metrics & status transitions
│   ├── routes/
│   │   ├── auth.py             # User profile sync & me endpoint
│   │   ├── subjects.py         # Academic subject catalog
│   │   ├── notes.py            # Public list, upload, details, download
│   │   └── admin.py            # Admin statistics & moderation queue
│   └── tests/
│       ├── test_validators.py  # Unit tests for magic bytes & size limits
│       └── test_routes.py      # End-to-end upload & moderation tests
├── scripts/
│   ├── seed_subjects.py        # Seed Sem 1-8 subjects into Firestore
│   └── seed_admin.py           # Promote user to administrator role
├── docs/
│   ├── PRD.md                  # Product Requirements Document v1.1
│   ├── UI_UX_Specification.md  # UI/UX Design System Specification v1.0
│   ├── Database_Design.md      # Firestore NoSQL Schema & Indexing Guide
│   └── Final_Tech_Stack.md     # Technology Stack Specification
├── .gitignore
└── README.md
```

---

## 4. Setup & Installation

### Step 1: Clone and Navigate
```bash
cd "NoteSphere"
```

### Step 2: Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 3: Configure Environment Variables
Copy the template file to `.env`:
```bash
copy backend\.env.example .env
```
Fill in your credentials in `.env`:
* **Cloudinary**: Get `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET` from [Cloudinary Console](https://console.cloudinary.com).
* **Firebase**: Download your service account key from **Firebase Console -> Project Settings -> Service accounts -> Generate new private key** and save it as `backend/serviceAccountKey.json`.
* **Frontend Firebase**: Update `frontend/js/firebase-config.js` with your Web App config.

*(Note: NoteSphere includes a built-in development fallback so you can boot and test the complete app, upload workflow, and moderation immediately even before pasting cloud keys!)*

### Step 4: Seed Subjects (Optional)
```bash
python scripts/seed_subjects.py
```

### Step 5: Start NoteSphere Application
```bash
python backend/app.py
```
Open your browser at: **`http://localhost:5000`**

---

## 5. Running Automated Tests

Run the full automated test suite verifying PDF magic bytes, validation rules, token verification, atomic upload rollback, and moderation lifecycles:

```bash
python -m unittest discover -s backend/tests -p "test_*.py"
```

All 15 tests pass out-of-the-box!

---

## 6. REST API Specification

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| `GET` | `/api/health` | Public | System health check & cloud service status |
| `GET` | `/api/subjects` | Public | List subjects, optionally filtered by `?semester=1..8` |
| `GET` | `/api/notes` | Public | List approved notes (`?search=&subject=&semester=&sort=`) |
| `GET` | `/api/notes/<id>` | Public | Get note details (approved only unless uploader/admin) |
| `POST` | `/api/notes` | Student / Admin | Upload PDF to Cloudinary + create pending record in Firestore |
| `GET` | `/api/my-notes` | Authenticated | List all submissions belonging to current user |
| `GET` | `/api/notes/<id>/download` | Public | Check approval, increment count, deliver authorized file |
| `POST` | `/api/auth/sync` | Authenticated | Sync Firebase user profile into Firestore `users` collection |
| `GET` | `/api/auth/me` | Authenticated | Get current user's profile and verified server role |
| `GET` | `/api/admin/stats` | Admin | Dashboard metrics (total, pending, approved, downloads) |
| `GET` | `/api/admin/notes` | Admin | Moderation queue (`?status=pending\|approved\|rejected`) |
| `PATCH` | `/api/admin/notes/<id>` | Admin | Approve or reject a note with optional reason |
| `DELETE` | `/api/admin/notes/<id>` | Admin | Permanently purge note and Cloudinary PDF asset |

---

## 7. Cloud Computing Principles Demonstrated

1. **Cloud Identity & Access Management (IAM):** Token-based authentication using Firebase Authentication and server-side zero-trust role verification.
2. **Cloud NoSQL Database:** Document-oriented schema design in Cloud Firestore with server timestamps and atomic counters.
3. **Cloud Object & Asset Storage:** Cloudinary storage for binary PDF assets with automatic URL generation and asset lifecycle coordination.
4. **Resilient Microservice Patterns:** Two-phase commit and atomic rollback (destroying Cloudinary orphans if database writes fail).
5. **Decoupled Architecture:** Separation of static frontend, RESTful compute backend, managed database, and specialized asset CDN.

---

## 8. License
Academic project built for Semester 5 Cloud Computing Mini Project (2026).
