<#
Usage: run this script locally to rewrite git history and remove committed secrets.

Important: This rewrites git history. You must coordinate with your team and rotate any secrets
before or immediately after running this. After rewriting, you will need to force-push and all
collaborators must re-clone or reset their local branch to avoid conflicts.

Steps inside this script:
1. Rotate keys on remote services (OpenAI/Fashn) and update your local .env.
2. Install git-filter-repo via pip.
3. Create a mirrored clone of the repo.
4. Create a replacements file containing the secrets to remove.
5. Run git-filter-repo to replace secrets and remove __pycache__ and .pyc.
6. Force push the cleaned mirror to origin.
#>

param(
    [string]$RepoUrl = $(git remote get-url origin),
    [switch]$Auto
)

Write-Host "Remote URL: $RepoUrl"

Write-Host "1) Please rotate any exposed keys first (OpenAI, Fashn)."
Write-Host "   Do this in the external service dashboards, not in git."
pause

Write-Host "2) Installing git-filter-repo if missing..."
python -m pip install --user git-filter-repo

Write-Host "3) Create a mirrored clone (safe workspace)..."
$mirrorDir = "$(Get-Location)\dhyun-mirror"
if (Test-Path $mirrorDir) {
    Write-Host "Mirror dir already exists. Remove or rename it and re-run." ; exit
}

git clone --mirror $RepoUrl $mirrorDir
Set-Location $mirrorDir

Write-Host "4) Edit replacements.txt and paste each secret token as 'old=>***REDACTED***'."
Write-Host "   Example lines (replace values with your keys):"
Write-Host "   sk-proj-XXXXX==>***REDACTED***"
Write-Host "   fa-XXXXX==>***REDACTED***"
Write-Host "   You can also place only the secret on each line (to remove occurrences)."

$repFile = Join-Path $mirrorDir "replacements.txt"
if (-Not (Test-Path $repFile)) { New-Item $repFile -ItemType File -Force | Out-Null }
if ($Auto) {
    Write-Host "Auto mode enabled: adding common secret tokens to replacements.txt"
    $secrets = @(
        'sk-proj-',
        'sk-',
        'fa-O9nz'
    )
    foreach ($s in $secrets) {
        # Replace all occurrences with a short placeholder
        Add-Content -Path $repFile -Value "$s==>***REDACTED***"
    }
    Write-Host "Auto replacements written to $repFile"
} else {
    Write-Host "Edit file: $repFile then press Enter to continue..."
    pause
}

Write-Host "5) Running git-filter-repo --replace-text $repFile"
python -m git_filter_repo --replace-text "$repFile"

Write-Host "6) Remove compiled Python and cache artifacts from history"
python -m git_filter_repo --invert-paths --paths __pycache__ --paths-glob "**/*.pyc"

Write-Host "7) Garbage collection to compress repo"
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host "8) Force push cleaned repository to origin. This will rewrite remote history."
Write-Host "   THIS WILL FORCE PUSH; make sure this is intended."
pause

git push --force --all
git push --force --tags

Write-Host "Done. Inform team to re-clone or reset to avoid history conflicts."