#!/bin/bash
set -e

echo "=" * 70
echo "Checking for conflicts between main and dev branches"
echo "=" * 70

# Fetch latest
echo ""
echo "1. Fetching latest from remote..."
git fetch --all

# Update main
echo ""
echo "2. Updating main branch..."
git checkout main
git pull origin main

# Update dev
echo ""
echo "3. Updating dev branch..."
git checkout dev
git pull origin dev

# Compare commits
echo ""
echo "4. Comparing branches..."
MAIN_COMMIT=$(git rev-parse main)
DEV_COMMIT=$(git rev-parse dev)
MERGE_BASE=$(git merge-base main dev)

echo "   Main commit:    $MAIN_COMMIT"
echo "   Dev commit:     $DEV_COMMIT"
echo "   Merge base:     $MERGE_BASE"

# Check if they're the same
if [ "$MAIN_COMMIT" = "$DEV_COMMIT" ]; then
    echo ""
    echo "✓ Main and dev are at the same commit - fully synced!"
    exit 0
fi

# Count commits
echo ""
echo "5. Commit differences:"
AHEAD=$(git rev-list --count main..dev 2>/dev/null || echo "0")
BEHIND=$(git rev-list --count dev..main 2>/dev/null || echo "0")
echo "   Commits in dev but not in main: $AHEAD"
echo "   Commits in main but not in dev: $BEHIND"

# Check for merge conflicts
echo ""
echo "6. Testing merge (dry run)..."
git merge --no-commit --no-ff main > /tmp/merge_test.log 2>&1
MERGE_EXIT_CODE=$?

if [ $MERGE_EXIT_CODE -eq 0 ]; then
    echo "   ✓ No conflicts detected - branches can merge cleanly"
    git merge --abort
    echo ""
    echo "=" * 70
    echo "Result: No conflicts found!"
    echo "=" * 70
    echo ""
    echo "To merge main into dev:"
    echo "  git checkout dev"
    echo "  git merge main"
    echo "  git push origin dev"
else
    echo "   ✗ Conflicts detected!"
    echo ""
    echo "   Conflict details:"
    cat /tmp/merge_test.log | grep -A 5 -i conflict || cat /tmp/merge_test.log
    git merge --abort 2>/dev/null || true
    echo ""
    echo "=" * 70
    echo "Result: Conflicts found!"
    echo "=" * 70
    echo ""
    echo "Conflicting files:"
    git diff --name-only --diff-filter=U main...dev 2>/dev/null || git diff --name-only main dev | head -10
    echo ""
    echo "To resolve conflicts:"
    echo "  1. git checkout dev"
    echo "  2. git merge main"
    echo "  3. Resolve conflicts in the files listed above"
    echo "  4. git add <resolved-files>"
    echo "  5. git commit"
    echo "  6. git push origin dev"
    exit 1
fi

# Show file differences
echo ""
echo "7. Files that differ between main and dev:"
git diff --name-status main...dev | head -20 || echo "   (no differences or error checking)"

echo ""
echo "=" * 70

