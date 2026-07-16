#!/usr/bin/env bash
# KARIS OS™ Version 1.0.0-PROD-V1 — Bash GitHub Linking & Push Automation Script
# Usage: ./scripts/link_and_push_to_github.sh <GITHUB_USERNAME> [GITHUB_PAT_TOKEN] [REPO_NAME]

set -e

USERNAME=$1
TOKEN=$2
REPO=${3:-"karis-os-core"}

if [ -z "$USERNAME" ]; then
    echo "Usage: $0 <GITHUB_USERNAME> [GITHUB_PAT_TOKEN] [REPO_NAME]"
    echo "Example: $0 johndoe ghp_YourPersonalAccessToken123 karis-os-core"
    exit 1
fi

echo "=========================================================================================="
echo "    KARIS OS™ GITHUB ACCOUNT LINKING & PUSH ENGINE"
echo "    Target Repository: https://github.com/$USERNAME/$REPO"
echo "=========================================================================================="

cd "$(dirname "$0")/.."

git remote remove origin 2>/dev/null || true

if [ -n "$TOKEN" ]; then
    git remote add origin "https://$USERNAME:$TOKEN@github.com/$USERNAME/$REPO.git"
else
    git remote add origin "https://github.com/$USERNAME/$REPO.git"
fi

git branch -M main
git log --oneline -n 5

echo ""
echo "Pushing complete commit history to remote GitHub repository..."
git push -u origin main --force

echo "✔ Successfully linked and pushed repository to https://github.com/$USERNAME/$REPO"
