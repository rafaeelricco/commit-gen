import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from importlib.metadata import PackageNotFoundError, version
from typing import Union

import requests
from packaging.version import Version

from common.base import BaseFrozen
from common.config import get_config_dir
from common.result import Err, Ok, Result

PACKAGE_NAME = "quick-assistant"
PYPI_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
CHECK_INTERVAL = 3600 * 24
CACHE_FILE = get_config_dir() / "update-cache.json"
UV_TOOL_PATH_PART = "uv"
UV_TOOL_NAME = "quick-assistant"
WINDOWS_DELAY_SECONDS = 2


# Error Types
class NetworkError(BaseFrozen):
    url: str
    message: str


class VersionCheckError(BaseFrozen):
    message: str


class PackageNotInstalled(BaseFrozen):
    package: str


class SubprocessError(BaseFrozen):
    command: str
    exit_code: int
    stderr: str


class CacheError(BaseFrozen):
    path: str
    message: str


UpdateError = Union[NetworkError, VersionCheckError, PackageNotInstalled, SubprocessError, CacheError]


def format_update_error(error: UpdateError) -> str:
    match error:
        case NetworkError(url=url, message=msg):
            return f"Network error fetching {url}: {msg}"
        case VersionCheckError(message=msg):
            return f"Version check failed: {msg}"
        case PackageNotInstalled(package=pkg):
            return f"Package '{pkg}' not installed"
        case SubprocessError(command=cmd, exit_code=code, stderr=err):
            return f"Command '{cmd}' failed (exit {code}): {err.strip()}"
        case CacheError(path=path, message=msg):
            return f"Cache error at {path}: {msg}"
        case _:
            return "Unknown error"


def get_current_version() -> Result[PackageNotInstalled, str]:
    try:
        return Result.ok(version(PACKAGE_NAME))
    except PackageNotFoundError:
        return Result.err(PackageNotInstalled(package=PACKAGE_NAME))


def get_latest_version() -> Result[Union[NetworkError, VersionCheckError], str]:
    try:
        response = requests.get(PYPI_URL, timeout=3)
        response.raise_for_status()
    except requests.RequestException as e:
        return Result.err(NetworkError(url=PYPI_URL, message=str(e)))

    try:
        data = response.json()
        return Result.ok(data["info"]["version"])
    except (json.JSONDecodeError, KeyError) as e:
        return Result.err(VersionCheckError(message=f"Invalid PyPI response: {e}"))


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


def update_package() -> Result[SubprocessError, None]:
    """Attempt to update via uv tool (if installed that way), then pipx, then pip.

    Handles missing executables (e.g., uv or pipx not in PATH) gracefully.
    On Windows, schedules the update in a detached shell with a short delay to avoid
    file-lock errors on the running quick.exe.
    """

    def run_command(cmd: list[str]) -> Result[SubprocessError, subprocess.CompletedProcess[str]]:
        try:
            completed = subprocess.run(cmd, capture_output=True, text=True)
            return Result.ok(completed)
        except FileNotFoundError as e:
            return Result.err(SubprocessError(command=" ".join(cmd), exit_code=127, stderr=str(e)))

    def run_detached_windows(
        cmd: list[str], delay_seconds: int = WINDOWS_DELAY_SECONDS
    ) -> Result[SubprocessError, None]:
        """Launch a command after a short delay so the current process can exit."""

        def quote(arg: str) -> str:
            return f'"{arg}"' if " " in arg else arg

        quoted_cmd = " ".join(quote(c) for c in cmd)
        delay = f"timeout /t {delay_seconds} /nobreak >nul"
        full_cmd = ["cmd", "/c", "start", "", "/b", "cmd", "/c", f"{delay} & {quoted_cmd}"]

        try:
            subprocess.Popen(full_cmd)
            return Result.ok(None)
        except Exception as e:
            return Result.err(SubprocessError(command=" ".join(cmd), exit_code=1, stderr=str(e)))

    def is_uv_tool_install() -> bool:
        exe_path = Path(sys.executable).resolve()
        parts = [p.lower() for p in exe_path.parts]
        return UV_TOOL_PATH_PART in parts and "tools" in parts and UV_TOOL_NAME in parts

    uv_cmd = ["uv", "tool", "install", PACKAGE_NAME, "--force"]
    pipx_cmd = ["pipx", "upgrade", PACKAGE_NAME]
    pip_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME]

    is_windows = platform.system() == "Windows"

    if is_windows:
        if is_uv_tool_install():
            uv_detached = run_detached_windows(uv_cmd)
            match uv_detached.inner:
                case Ok():
                    return Result.ok(None)
                case Err():
                    pass

        pipx_detached = run_detached_windows(pipx_cmd)
        match pipx_detached.inner:
            case Ok():
                return Result.ok(None)
            case Err():
                pass

        pip_detached = run_detached_windows(pip_cmd)
        match pip_detached.inner:
            case Ok():
                return Result.ok(None)
            case Err(error=err):
                return Result.err(err)

    else:
        if is_uv_tool_install():
            uv_result = run_command(uv_cmd)
            match uv_result.inner:
                case Ok(value=cp) if cp.returncode == 0:
                    return Result.ok(None)
                case _:
                    # Ignore uv failures and try other managers
                    pass

        pipx_result = run_command(pipx_cmd)
        match pipx_result.inner:
            case Ok(value=cp) if cp.returncode == 0:
                return Result.ok(None)
            case _:
                # Ignore pipx failures (missing or error) and try pip next
                pass

        pip_result = run_command(pip_cmd)
        match pip_result.inner:
            case Ok(value=cp) if cp.returncode == 0:
                return Result.ok(None)
            case Ok(value=cp):
                stderr = cp.stderr or cp.stdout or "Unknown error"
                return Result.err(SubprocessError(command=" ".join(pip_cmd), exit_code=cp.returncode, stderr=stderr))
            case Err(error=err):
                return Result.err(err)


def check_and_update() -> None:
    if not should_check_update():
        return

    save_check_timestamp()

    current_result = get_current_version()
    match current_result.inner:
        case Err():
            return
        case Ok(value=current):
            pass

    latest_result = get_latest_version()
    match latest_result.inner:
        case Err():
            return
        case Ok(value=latest):
            pass

    if Version(latest) > Version(current):
        print(f"Updating quick-assistant {current} → {latest}...")
        update_result = update_package()
        match update_result.inner:
            case Ok():
                if platform.system() == "Windows":
                    print("Update started in the background. Please re-run the command in a few seconds.")
                else:
                    print("Update complete. Please restart the command.")
                sys.exit(0)
            case Err(error=error):
                print(f"Auto-update failed: {format_update_error(error)}")


def execute_update() -> int:
    current_result = get_current_version()
    match current_result.inner:
        case Err(error=current_err):
            print(f"Error: {format_update_error(current_err)}")
            return 1
        case Ok(value=current):
            pass

    latest_result = get_latest_version()
    match latest_result.inner:
        case Err(error=latest_err):
            print(f"Error: {format_update_error(latest_err)}")
            return 1
        case Ok(value=latest):
            pass

    if Version(latest) <= Version(current):
        print(f"Already at latest version ({current}).")
        return 0

    print(f"Updating quick-assistant {current} → {latest}...")
    update_result = update_package()
    match update_result.inner:
        case Ok():
            if platform.system() == "Windows":
                print("Update started in the background. Please re-run the command in a few seconds.")
            else:
                print("Update complete!")
            return 0
        case Err(error=update_err):
            print(f"Update failed: {format_update_error(update_err)}")
            return 1
