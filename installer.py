"""Small Windows-friendly bootstrap installer."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    print("Buffett Value Lab — installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
    print("\nDone. Start the app with: python main.py")


if __name__ == "__main__":
    main()
