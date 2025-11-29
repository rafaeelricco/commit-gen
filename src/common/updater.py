import json
import subprocess
import sys
import time
from importlib.metadata import version
from typing import Optional

import requests
from packaging.version import Version

from common.config import get_config_dir

PACKAGE_NAME = "quick-assistant"
PYPI_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
CHECK_INTERVAL = 3600 * 24
CACHE_FILE = get_config_dir() / "update-cache.json"


def get_current_version() -> str:
    return version(PACKAGE_NAME)


def get_latest_version() -> Optional[str]:
    try:
        response = requests.get(PYPI_URL, timeout=3)
        response.raise_for_status()
        return response.json()["info"]["version"]
    except Exception:
        return None


def should_check_update() -> bool:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not CACHE_FILE.exists():
        return True

    try:
        data = json.loads(CACHE_FILE.read_text())
        last_check = data.get("last_check", 0)
        return time.time() - last_check > CHECK_INTERVAL
    except Exception:
        return True


def save_check_timestamp() -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({"last_check": time.time()}))


def update_package() -> bool:
    try:
        result = subprocess.run(["pipx", "upgrade", PACKAGE_NAME], capture_output=True, text=True)
        if result.returncode == 0:
            return True

        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME], capture_output=True, check=True
        )
        return True
    except Exception:
        return False


def check_and_update() -> None:
    if not should_check_update():
        return

    save_check_timestamp()

    try:
        current = get_current_version()
    except Exception:
        return

    latest = get_latest_version()

    if latest is None or current == latest:
        return

    if Version(latest) > Version(current):
        print(f"Updating quick-assistant {current} → {latest}...")
        if update_package():
            print("Update complete. Please restart the command.")
            sys.exit(0)


def execute_update() -> int:
    try:
        current = get_current_version()
    except Exception:
        print("Error: Could not determine current version.")
        return 1

    latest = get_latest_version()
    if latest is None:
        print("Error: Could not fetch latest version from PyPI.")
        return 1

    if Version(latest) <= Version(current):
        print(f"Already at latest version ({current}).")
        return 0

    print(f"Updating quick-assistant {current} → {latest}...")
    if update_package():
        print("Update complete!")
        return 0
    else:
        print("Update failed.")
        return 1
