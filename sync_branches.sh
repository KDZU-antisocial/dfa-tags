#!/bin/bash
set -e

echo "=" * 70
echo "Syncing main and dev branches"
echo "=" * 70

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Fetch all from remote
echo ""
echo "Fetching from remote..."
git fetch --all

# Check if dev branch exists locally
if git show-ref --verify --quiet refs/heads/dev; then
    echo "✓ dev branch exists locally"
    HAS_LOCAL_DEV=true
else
    echo "⚠ dev branch does not exist locally"
    HAS_LOCAL_DEV=false
fi

# Check if dev branch exists on remote
if git show-ref --verify --quiet refs/remotes/origin/dev; then
    echo "✓ dev branch exists on remote"
    HAS_REMOTE_DEV=true
else
    echo "⚠ dev branch does not exist on remote"
    HAS_REMOTE_DEV=false
fi

# Ensure we're on main and it's up to date
echo ""
echo "Updating main branch..."
git checkout main
git pull origin main

# Handle dev branch
echo ""
if [ "$HAS_REMOTE_DEV" = true ]; then
    if [ "$HAS_LOCAL_DEV" = true ]; then
        echo "Checking out dev branch..."
        git checkout dev
        echo "Pulling latest dev from remote..."
        git pull origin dev || echo "Warning: Could not pull dev (may have conflicts)"
        
        # Compare main and dev
        echo ""
        echo "Comparing main and dev..."
        MAIN_COMMIT=$(git rev-parse main)
        DEV_COMMIT=$(git rev-parse dev)
        
        if [ "$MAIN_COMMIT" = "$DEV_COMMIT" ]; then
            echo "✓ main and dev are at the same commit - fully synced!"
        else
            # Check if dev is ahead/behind main
            MERGE_BASE=$(git merge-base main dev)
            if [ "$MERGE_BASE" = "$MAIN_COMMIT" ]; then
                echo "⚠ dev is ahead of main"
                AHEAD=$(git rev-list --count main..dev)
                echo "  dev is $AHEAD commits ahead of main"
            elif [ "$MERGE_BASE" = "$DEV_COMMIT" ]; then
                echo "⚠ dev is behind main"
                BEHIND=$(git rev-list --count dev..main)
                echo "  dev is $BEHIND commits behind main"
            else
                echo "⚠ main and dev have diverged"
                AHEAD=$(git rev-list --count main..dev)
                BEHIND=$(git rev-list --count dev..main)
                echo "  dev is $AHEAD commits ahead, $BEHIND commits behind main"
            fi
            
            # Try to merge main into dev to check for conflicts
            echo ""
            echo "Testing merge of main into dev (dry run)..."
            git merge --no-commit --no-ff main || MERGE_FAILED=true
            if [ "$MERGE_FAILED" = true ]; then
                echo "✗ Potential conflicts detected!"
                git merge --abort 2>/dev/null || true
                echo ""
                echo "To resolve conflicts manually:"
                echo "  1. git checkout dev"
                echo "  2. git merge main"
                echo "  3. Resolve conflicts"
                echo "  4. git commit"
            else
                echo "✓ No conflicts detected - branches can be merged"
                git merge --abort 2>/dev/null || true
            fi
        fi
    else
        echo "Creating local dev branch from remote..."
        git checkout -b dev origin/dev
        echo "✓ dev branch created and checked out"
    fi
else
    echo "⚠ No dev branch on remote. Creating new dev branch from main..."
    if [ "$HAS_LOCAL_DEV" = true ]; then
        git checkout dev
        echo "Local dev branch exists but no remote. Consider pushing it."
    else
        git checkout -b dev
        echo "✓ Created new dev branch from main"
    fi
fi

echo ""
echo "=" * 70
echo "Summary:"
echo "=" * 70
git branch -vv
echo ""
echo "Current branch: $(git branch --show-current)"

