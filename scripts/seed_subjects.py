"""
Script to seed initial subjects into Cloud Firestore.
Run using: python scripts/seed_subjects.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import firestore_db, firebase_configured

SUBJECTS_DATA = [
    # Semester 1
    {"id": "cs-sem1-math1", "name": "Engineering Mathematics I", "subjectCode": "MATH101", "departmentId": "computer-engineering", "semester": 1, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem1-phy", "name": "Engineering Physics", "subjectCode": "PHY101", "departmentId": "computer-engineering", "semester": 1, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem1-bee", "name": "Basic Electrical Engineering", "subjectCode": "EE101", "departmentId": "computer-engineering", "semester": 1, "courseName": "B.Tech Computer Engineering"},
    # Semester 2
    {"id": "cs-sem2-math2", "name": "Engineering Mathematics II", "subjectCode": "MATH201", "departmentId": "computer-engineering", "semester": 2, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem2-cprog", "name": "Programming in C", "subjectCode": "CS102", "departmentId": "computer-engineering", "semester": 2, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem2-chem", "name": "Engineering Chemistry", "subjectCode": "CH201", "departmentId": "computer-engineering", "semester": 2, "courseName": "B.Tech Computer Engineering"},
    # Semester 3
    {"id": "cs-sem3-dsa", "name": "Data Structures & Algorithms", "subjectCode": "CS301", "departmentId": "computer-engineering", "semester": 3, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem3-co", "name": "Computer Organization & Architecture", "subjectCode": "CS302", "departmentId": "computer-engineering", "semester": 3, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem3-oop", "name": "Object-Oriented Programming with Java", "subjectCode": "CS303", "departmentId": "computer-engineering", "semester": 3, "courseName": "B.Tech Computer Engineering"},
    # Semester 4
    {"id": "cs-sem4-dbms", "name": "Database Management Systems", "subjectCode": "CS401", "departmentId": "computer-engineering", "semester": 4, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem4-os", "name": "Operating Systems", "subjectCode": "CS402", "departmentId": "computer-engineering", "semester": 4, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem4-toc", "name": "Theory of Computation", "subjectCode": "CS403", "departmentId": "computer-engineering", "semester": 4, "courseName": "B.Tech Computer Engineering"},
    # Semester 5
    {"id": "cs-sem5-cn", "name": "Computer Networks", "subjectCode": "CS501", "departmentId": "computer-engineering", "semester": 5, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem5-cc", "name": "Cloud Computing", "subjectCode": "CS502", "departmentId": "computer-engineering", "semester": 5, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem5-wt", "name": "Web Technologies", "subjectCode": "CS503", "departmentId": "computer-engineering", "semester": 5, "courseName": "B.Tech Computer Engineering"},
    # Semester 6
    {"id": "cs-sem6-se", "name": "Software Engineering", "subjectCode": "CS601", "departmentId": "computer-engineering", "semester": 6, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem6-ai", "name": "Artificial Intelligence", "subjectCode": "CS602", "departmentId": "computer-engineering", "semester": 6, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem6-cd", "name": "Compiler Design", "subjectCode": "CS603", "departmentId": "computer-engineering", "semester": 6, "courseName": "B.Tech Computer Engineering"},
    # Semester 7
    {"id": "cs-sem7-ml", "name": "Machine Learning", "subjectCode": "CS701", "departmentId": "computer-engineering", "semester": 7, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem7-bct", "name": "Blockchain Technology", "subjectCode": "CS702", "departmentId": "computer-engineering", "semester": 7, "courseName": "B.Tech Computer Engineering"},
    # Semester 8
    {"id": "cs-sem8-cns", "name": "Cyber & Information Security", "subjectCode": "CS801", "departmentId": "computer-engineering", "semester": 8, "courseName": "B.Tech Computer Engineering"},
    {"id": "cs-sem8-iot", "name": "Internet of Things", "subjectCode": "CS802", "departmentId": "computer-engineering", "semester": 8, "courseName": "B.Tech Computer Engineering"}
]

def seed_subjects():
    if not firebase_configured or not firestore_db:
        print("[!] Live Firebase not configured. Subjects are already bundled in local in-memory fallback store.")
        print("[*] To seed into live Firestore, ensure backend/serviceAccountKey.json is placed and run this script again.")
        return

    import firebase_admin.firestore as f_store
    print(f"[*] Seeding {len(SUBJECTS_DATA)} subjects into Cloud Firestore collection 'subjects'...")
    batch = firestore_db.batch()

    for item in SUBJECTS_DATA:
        sub_id = item["id"]
        doc_ref = firestore_db.collection("subjects").document(sub_id)
        doc_data = {
            "name": item["name"],
            "normalizedName": item["name"].lower(),
            "subjectCode": item["subjectCode"],
            "departmentId": item["departmentId"],
            "semester": item["semester"],
            "courseName": item["courseName"],
            "isActive": True,
            "createdAt": f_store.SERVER_TIMESTAMP,
            "updatedAt": f_store.SERVER_TIMESTAMP
        }
        batch.set(doc_ref, doc_data, merge=True)

    batch.commit()
    print("[+] Successfully seeded all subjects into Cloud Firestore!")

if __name__ == "__main__":
    seed_subjects()
