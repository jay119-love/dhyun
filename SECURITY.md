# Security instructions

This project uses environment variables for secrets. Avoid committing keys in repository or history.

If a secret is accidentally committed, follow one of these workflows to remove it:

1) Prefered: rotate the secret (revoke the leaked key) in the service dashboard (OpenAI, Fashn) immediately.
2) Use `git-filter-repo` or `bfg` to rewrite git history and remove secrets from old commits.
3) Remove compiled artifacts from history (e.g. `__pycache__`, `.pyc`).
4) Force push the cleaned repository to remote and have other developers re-clone or reset.

Example commands are in `scripts/cleanup_secrets.ps1` (PowerShell). Use with care.
