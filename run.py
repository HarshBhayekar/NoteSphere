"""
NoteSphere - Main Application Launcher
Run with: python run.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import app
from backend.config import PORT

if __name__ == "__main__":
    print(f"\n========================================================")
    print(f"  NoteSphere: Cloud-Based Notes Sharing Platform")
    print(f"  Server running at: http://localhost:{PORT}")
    print(f"========================================================\n")
    app.run(host="0.0.0.0", port=PORT, debug=True)
