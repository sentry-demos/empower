#!/bin/bash

# Setup script to install git hooks for local.env management
# This script creates symlinks from .git/hooks/ to the tracked hook files in _bin/
# Idempotent: can be run multiple times safely

set -e

# Get the repository root directory
REPO_ROOT=$(git rev-parse --show-toplevel)
BIN_DIR="$REPO_ROOT/_bin"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

# Check if we're in a git repository
if [ ! -d "$HOOKS_DIR" ]; then
    echo "Error: Not in a git repository or .git/hooks directory not found"
    exit 1
fi

# Check if _bin directory exists
if [ ! -d "$BIN_DIR" ]; then
    echo "Error: _bin directory not found"
    exit 1
fi

# Function to check if a hook is properly set up
is_hook_setup() {
    local hook_name="$1"
    local source_file="$BIN_DIR/$hook_name"
    local target_file="$HOOKS_DIR/$hook_name"
    
    # Check if target is a symlink pointing to the correct source
    if [ -L "$target_file" ] && [ "$(readlink "$target_file")" = "$source_file" ]; then
        # Also check if it's executable
        if [ -x "$target_file" ]; then
            return 0  # Hook is properly set up
        fi
    fi
    return 1  # Hook needs setup
}

# Function to install a hook
install_hook() {
    local hook_name="$1"
    local source_file="$BIN_DIR/$hook_name"
    local target_file="$HOOKS_DIR/$hook_name"
    
    if [ ! -f "$source_file" ]; then
        echo "Warning: $source_file not found, skipping $hook_name"
        return 1
    fi
    
    # Remove existing hook if it exists and is not properly set up
    if [ -f "$target_file" ] || [ -L "$target_file" ]; then
        if ! is_hook_setup "$hook_name"; then
            echo "Removing existing $hook_name hook..."
            rm "$target_file"
        else
            echo "✓ $hook_name hook already properly set up"
            return 0
        fi
    fi
    
    # Create symlink to the tracked hook file
    echo "Installing $hook_name hook..."
    ln -s "$source_file" "$target_file"
    
    # Make sure it's executable
    chmod +x "$target_file"
    
    echo "✓ $hook_name hook installed successfully"
}

# Check if all hooks are already properly set up
all_hooks_setup=true
for hook in "merge-local-env" "post-merge" "post-checkout"; do
    if ! is_hook_setup "$hook"; then
        all_hooks_setup=false
        break
    fi
done

if [ "$all_hooks_setup" = true ]; then
    echo "✓ All git hooks are already properly set up"
    echo "  • post-merge    - Runs after git merge, git pull (without --rebase)"
    echo "  • post-checkout - Runs after git checkout, git switch, git pull --rebase, git clone"
    exit 0
fi

echo "Setting up git hooks for local.env management..."

# Install the hooks
install_hook "merge-local-env"
install_hook "post-merge"
install_hook "post-checkout"

echo ""
echo "🎉 Git hooks setup complete!"
echo ""
echo "The following hooks are now active:"
echo "  • post-merge    - Runs after git merge, git pull (without --rebase)"
echo "  • post-checkout - Runs after git checkout, git switch, git pull --rebase, git clone"
echo ""
echo "These hooks will automatically:"
echo "  • Create local.env from local.env.base if it doesn't exist"
echo "  • Merge upstream changes from local.env.base into local.env"
echo "  • Warn about conflicts that need manual resolution"
echo ""
echo "To remove the hooks, run:"
echo "  rm $HOOKS_DIR/post-merge $HOOKS_DIR/post-checkout $HOOKS_DIR/merge-local-env"
