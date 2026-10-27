"""
Script to promote or seed an administrator user in Cloud Firestore.
Usage:
    python scripts/seed_admin.py <firebase_uid> [optional_email] [optional_display_name]
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import firestore_db, firebase_configured

def make_admin(uid, email=None, display_name=None):
    if not firebase_configured or not firestore_db:
        print("[!] Live Firebase not configured. In dev mode, use emails listed in ADMIN_EMAILS or dev-token-admin-<uid>.")
        return

    import firebase_admin.firestore as f_store
    user_ref = firestore_db.collection("users").document(uid)
    doc = user_ref.get()

    if doc.exists:
        user_ref.update({
            "role": "admin",
            "updatedAt": f_store.SERVER_TIMESTAMP
        })
        print(f"[+] Successfully promoted existing user '{uid}' to role: admin")
    else:
        user_ref.set({
            "uid": uid,
            "displayName": display_name or (email.split("@")[0] if email else "Admin"),
            "email": email or "admin@notesphere.edu",
            "role": "admin",
            "departmentId": "computer-engineering",
            "isActive": True,
            "createdAt": f_store.SERVER_TIMESTAMP,
            "updatedAt": f_store.SERVER_TIMESTAMP
        })
        print(f"[+] Created and granted admin role to user '{uid}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed_admin.py <firebase_uid> [email] [displayName]")
        sys.exit(1)

    target_uid = sys.argv[1]
    target_email = sys.argv[2] if len(sys.argv) > 2 else None
    target_name = sys.argv[3] if len(sys.argv) > 3 else None
    make_admin(target_uid, target_email, target_name)
