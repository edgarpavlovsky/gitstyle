#!/bin/bash
# Simulated gitstyle pipeline output for demo recording
# This script produces realistic output matching what the real pipeline generates

echo ""
echo -e "\033[1;36mgitstyle v0.1.0\033[0m"
echo -e "Analyzing \033[1mkarpathy\033[0m's engineering style..."
echo ""

# Stage 1
echo -e "──────────────────── \033[1mStage 1: Fetch\033[0m ────────────────────"
sleep 0.5
echo -e "\033[1mFetching commits for \033[36mkarpathy\033[0m\033[1m...\033[0m"
sleep 0.3
for repo in "nanoGPT" "llm.c" "micrograd" "minbpe" "makemore"; do
    echo -e "  Fetching karpathy/$repo..."
    sleep 0.2
done
echo -e "\033[32mFetched 359 commits across 5 repos.\033[0m"
sleep 0.3

# Stage 2
echo ""
echo -e "──────────────────── \033[1mStage 2: Sample\033[0m ───────────────────"
sleep 0.3
echo "Fetching diffs for sampling..."
sleep 0.5
echo -e "\033[1mFormed 12 clusters from 359 commits.\033[0m"
echo -e "\033[32mSampled down to 316 representative commits.\033[0m"
sleep 0.3

# Stage 3
echo ""
echo -e "──────────────────── \033[1mStage 3: Extract\033[0m ──────────────────"
sleep 0.3
clusters=("nanoGPT:python" "llm.c:c" "micrograd:python" "minbpe:python" "makemore:python" "nanoGPT:config" "llm.c:cuda" "nanoGPT:data" "minbpe:tests" "llm.c:build" "makemore:notebooks" "nanoGPT:bench")
for i in "${!clusters[@]}"; do
    n=$((i + 1))
    obs=$((RANDOM % 8 + 5))
    echo -e "\033[1mExtracting [$n/12]: karpathy/${clusters[$i]} ...\033[0m"
    sleep 0.4
    echo -e "  \033[32m$obs observations\033[0m"
done
echo -e "\033[1;32mExtraction complete: 78 observations from 12 clusters.\033[0m"
sleep 0.3

# Stage 4
echo ""
echo -e "──────────────────── \033[1mStage 4: Compile\033[0m ──────────────────"
sleep 0.3
echo -e "\033[1mCompiling wiki articles...\033[0m"
for dim in "code-structure" "naming-conventions" "patterns" "type-discipline" "testing" "comments-and-docs" "dependencies" "commit-hygiene" "languages/python" "languages/c"; do
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
echo -e "\033[33mLint: 0 errors, 1 warning, 2 info\033[0m"
echo -e "  \033[33m[testing] No pytest/unittest usage — test patterns inferred\033[0m"
echo -e "    → Consider manual review of testing article"
echo -e "  \033[34m[general] Strong cross-repo consistency (single-author educational projects)\033[0m"
echo -e "  \033[34m[general] Two-language profile: Python (primary) + C (secondary)\033[0m"
sleep 0.3

# Write
echo ""
echo -e "──────────────────── \033[1mWriting Wiki\033[0m ─────────────────────"
sleep 0.2
for f in "code-structure.md" "naming-conventions.md" "patterns.md" "type-discipline.md" "testing.md" "comments-and-docs.md" "dependencies.md" "commit-hygiene.md" "languages/python.md" "languages/c.md" "index.md" "_meta/sources.md" "_meta/generation-config.md" "_meta/log.md"; do
    echo "  Wrote wiki/$f"
    sleep 0.1
done
sleep 0.3

echo ""
echo -e "\033[1;32m✓ Wiki generated at wiki/\033[0m"
echo "  10 articles across 5 repos"
echo ""
