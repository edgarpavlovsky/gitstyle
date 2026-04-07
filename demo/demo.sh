#!/bin/bash
# Simulated gitstyle pipeline output for demo recording
# This script produces realistic output matching what the real pipeline generates

echo ""
echo -e "\033[1;36mgitstyle v0.1.0\033[0m"
echo -e "Analyzing \033[1medgarpavlovsky\033[0m's engineering style..."
echo ""

# Stage 1
echo -e "──────────────────── \033[1mStage 1: Fetch\033[0m ────────────────────"
sleep 0.5
echo -e "\033[1mFetching commits for \033[36medgarpavlovsky\033[0m\033[1m...\033[0m"
sleep 0.3
for repo in "pulse-ios" "token-list" "yc-demo-day-countdown" "shipkit"; do
    echo -e "  Fetching edgarpavlovsky/$repo..."
    sleep 0.2
done
echo -e "\033[32mFetched 812 commits across 4 repos.\033[0m"
sleep 0.3

# Stage 2
echo ""
echo -e "──────────────────── \033[1mStage 2: Sample\033[0m ───────────────────"
sleep 0.3
echo "Fetching diffs for sampling..."
sleep 0.5
echo -e "\033[1mFormed 6 clusters from 812 commits.\033[0m"
echo -e "\033[32mSampled down to 94 representative commits.\033[0m"
sleep 0.3

# Stage 3
echo ""
echo -e "──────────────────── \033[1mStage 3: Extract\033[0m ──────────────────"
sleep 0.3
clusters=("pulse-ios:swift" "token-list:typescript" "yc-demo-day-countdown:swift" "shipkit:typescript" "shipkit:yaml" "token-list:json")
for i in "${!clusters[@]}"; do
    n=$((i + 1))
    obs=$((RANDOM % 8 + 5))
    echo -e "\033[1mExtracting [$n/6]: edgarpavlovsky/${clusters[$i]} ...\033[0m"
    sleep 0.4
    echo -e "  \033[32m$obs observations\033[0m"
done
echo -e "\033[1;32mExtraction complete: 42 observations from 6 clusters.\033[0m"
sleep 0.3

# Stage 4
echo ""
echo -e "──────────────────── \033[1mStage 4: Compile\033[0m ──────────────────"
sleep 0.3
echo -e "\033[1mCompiling wiki articles...\033[0m"
for dim in "code-structure" "naming-conventions" "patterns" "type-discipline" "testing" "comments-and-docs" "dependencies" "commit-hygiene" "languages/swift" "languages/typescript"; do
    echo "  Writing $dim..."
    sleep 0.3
done
echo -e "\033[32mCompiled 10 wiki articles.\033[0m"
sleep 0.3

# Stage 5
echo ""
echo -e "──────────────────── \033[1mStage 5: Lint\033[0m ────────────────────"
sleep 0.3
echo -e "\033[1mRunning lint pass on wiki articles...\033[0m"
sleep 0.5
echo -e "\033[33mLint: 0 errors, 2 warnings, 1 info\033[0m"
echo -e "  \033[33m[testing] Limited test evidence in public repos\033[0m"
echo -e "    → Consider analyzing private repos with GITHUB_TOKEN"
echo -e "  \033[33m[dependencies] Some dependency claims based on single repo\033[0m"
echo -e "    → Cross-reference with additional repositories"
echo -e "  \033[34m[general] Good cross-referencing between articles\033[0m"
sleep 0.3

# Write
echo ""
echo -e "──────────────────── \033[1mWriting Wiki\033[0m ─────────────────────"
sleep 0.2
for f in "code-structure.md" "naming-conventions.md" "patterns.md" "type-discipline.md" "testing.md" "comments-and-docs.md" "dependencies.md" "commit-hygiene.md" "languages/swift.md" "languages/typescript.md" "index.md" "_meta/sources.md" "_meta/generation-config.md" "_meta/log.md"; do
    echo "  Wrote wiki/$f"
    sleep 0.1
done
sleep 0.3

echo ""
echo -e "\033[1;32m✓ Wiki generated at wiki/\033[0m"
echo "  10 articles across 4 repos"
echo ""

