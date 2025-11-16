Write-Host "Removing tracked __pycache__ files and .pyc from the current branch"

git rm --cached -r __pycache__
git rm --cached -r *.pyc
git commit -m "chore: remove compiled python artifacts from tracking"

Write-Host "Added .gitignore — push the commit now."
Write-Host "Note: if the secret is still in historic commits, you must use git-filter-repo or BFG as in cleanup_secrets.ps1"