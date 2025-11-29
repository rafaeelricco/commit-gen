import os
import sys
from pathlib import Path
from importlib.metadata import version

PACKAGE_NAME = "quick-assistant"


def execute_doctor() -> int:
    """Diagnose installation and PATH issues."""
    print("Quick Assistant - System Diagnostics\n")

    try:
        current_version = version(PACKAGE_NAME)
    except Exception:
        current_version = "unknown"

    print(f"Version: {current_version}")
    print(f"Platform: {sys.platform}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Executable: {sys.executable}")

    if sys.platform == "win32":
        return _check_windows_path()

    print("\nPATH configuration typically works out-of-the-box on Unix systems.")
    return 0


def _check_windows_path() -> int:
    """Check Windows PATH configuration."""
    scripts_dir = Path(sys.executable).parent / "Scripts"
    pipx_bin = Path.home() / ".local" / "bin"
    path_env = os.environ.get("PATH", "")

    issues: list[tuple[str, Path]] = []

    if scripts_dir.exists() and str(scripts_dir).lower() not in path_env.lower():
        issues.append(("pip Scripts", scripts_dir))

    if pipx_bin.exists() and str(pipx_bin).lower() not in path_env.lower():
        issues.append(("pipx bin", pipx_bin))

    if not issues:
        print("\nPATH appears correctly configured.")
        return 0

    print("\nPATH issues detected:\n")
    for name, path in issues:
        print(f"  - {name} not in PATH: {path}")

    print("\nRemediation:")
    print("  1. For pipx installations:")
    print("     pipx ensurepath")
    print("")
    print("  2. For pip installations, add to PATH manually:")
    print(f'     setx PATH "%PATH%;{scripts_dir}"')
    print("")
    print("  3. Restart your terminal after making changes.")

    return 1
