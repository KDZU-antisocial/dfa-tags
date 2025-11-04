#!/bin/bash
echo "=== Branch Sync Status ==="
echo ""
echo "Current branch: $(git branch --show-current)"
echo ""
echo "Branch status:"
git branch -vv
echo ""
echo "Remote branches:"
git branch -r
echo ""
echo "Main and Dev commit comparison:"
MAIN_COMMIT=$(git rev-parse main)
DEV_COMMIT=$(git rev-parse dev)
echo "Main:  $MAIN_COMMIT"
echo "Dev:   $DEV_COMMIT"
echo ""
if [ "$MAIN_COMMIT" = "$DEV_COMMIT" ]; then
    echo "✓ Main and dev are synced (same commit)"
else
    echo "⚠ Main and dev are different"
    echo ""
    echo "Checking for conflicts..."
    git checkout dev > /dev/null 2>&1
    if git merge --no-commit --no-ff main > /dev/null 2>&1; then
        echo "✓ No conflicts detected - can merge cleanly"
        git merge --abort > /dev/null 2>&1
    else
        echo "✗ Potential conflicts - manual merge needed"
        git merge --abort > /dev/null 2>&1
    fi
fi

