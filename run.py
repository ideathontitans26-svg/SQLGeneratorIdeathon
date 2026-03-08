"""
Build frontend and run the full application (production mode).
Single command to host and run everything.
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_DIR = PROJECT_ROOT / "backend"


def main():
    # 1. Build frontend
    print("Building frontend...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND_DIR,
        shell=True,
    )
    if result.returncode != 0:
        print("Frontend build failed. Run 'npm run build' in frontend/ manually.")
        sys.exit(1)
    print("Frontend built successfully.\n")

    # 2. Run backend (serves API + static frontend)
    print("Starting server at http://localhost:8000")
    subprocess.run(
        [sys.executable, "run.py"],
        cwd=BACKEND_DIR,
        shell=True,
    )


if __name__ == "__main__":
    main()
