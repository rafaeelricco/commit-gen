#!/bin/bash

# =============================================================================
# Build Script for Commit Gen
# =============================================================================
#
# DESCRIPTION:
#   Builds and installs a clean version of the Commit Gen CLI tool.
#   Performs cleanup of any existing installations before building fresh.
#
# FEATURES:
#   • Cleans up any corrupted or existing installations
#   • Installs fresh CLI tool globally
#   • Provides clear visual feedback with status icons
#
# REQUIREMENTS:
#   • uv: Modern Python package manager
#
# USAGE:
#   ./dev/build.sh
#
# =============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "󰏖 Building Commit Gen CLI..."
echo ""

# =============================================================================
# FUNCTION: clean
# =============================================================================
# Removes any existing tool installation to ensure fresh install.
#
# BEHAVIOR:
#   1. Attempts clean uninstall via uv
#   2. Manually removes the tool directory as fallback
#
# PARAMETERS: None
# RETURNS: None
# =============================================================================
clean() {
    echo "󰅖 Cleaning existing installation..."
    uv tool uninstall commit-gen 2>/dev/null || true
    rm -rf ~/.local/share/uv/tools/commit-gen 2>/dev/null || true
}

# =============================================================================
# FUNCTION: build
# =============================================================================
# Performs clean build and installation of the Commit Gen CLI tool.
# 
# BEHAVIOR:
#   1. Cleans any existing installation
#   2. Installs the tool in editable mode
#   3. Retries on failure
#
# PARAMETERS: None
# RETURNS: None
# =============================================================================
build() {
    echo "󰏖 Installing global CLI..."
    clean
    
    if ! uv tool install -e . --force 2>/dev/null; then
        echo "󰅖 Installation failed, retrying..."
        uv tool install -e . --force
        uv tool update-shell
    fi
   
    echo "󰄬 Global 'commit' command ready"
    echo ""
}

# Main build process
build

echo "󰄬 Build complete! The 'commit' command is now available globally."
