#!/bin/bash
echo "=== Checking Local Branch Sync ==="
echo ""

# Get current branch
CURRENT=$(git branch --show-current)
echo "Current branch: $CURRENT"
echo ""

# Get commit hashes
MAIN_LOCAL=$(git rev-parse main 2>/dev/null)
DEV_LOCAL=$(git rev-parse dev 2>/dev/null)

if [ -z "$MAIN_LOCAL" ]; then
    echo "✗ Local main branch does not exist"
    exit 1
fi

if [ -z "$DEV_LOCAL" ]; then
    echo "✗ Local dev branch does not exist"
    exit 1
fi

echo "Local main commit: $MAIN_LOCAL"
echo "Local dev commit:  $DEV_LOCAL"
echo ""

# Compare commits
if [ "$MAIN_LOCAL" = "$DEV_LOCAL" ]; then
    echo "✓ Local main and dev are SYNCED (same commit)"
    echo ""
    echo "Commit info:"
    git log -1 --oneline main
else
    echo "⚠ Local main and dev are DIFFERENT"
    echo ""
    
    # Count differences
    AHEAD=$(git rev-list --count main..dev 2>/dev/null || echo "0")
    BEHIND=$(git rev-list --count dev..main 2>/dev/null || echo "0")
    
    echo "Commits in dev but not in main: $AHEAD"
    echo "Commits in main but not in dev: $BEHIND"
    echo ""
    
    if [ "$AHEAD" -gt 0 ] && [ "$BEHIND" -eq 0 ]; then
        echo "Status: dev is ahead of main"
    elif [ "$BEHIND" -gt 0 ] && [ "$AHEAD" -eq 0 ]; then
        echo "Status: main is ahead of dev"
    else
        echo "Status: branches have diverged"
    fi
    
    echo ""
    echo "Recent commits in main:"
    git log --oneline -3 main
    echo ""
    echo "Recent commits in dev:"
    git log --oneline -3 dev
fi

