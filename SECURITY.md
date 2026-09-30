# Security Policy

## Reporting a vulnerability

If you find a security issue in this project, please **do not** open a public
issue. Email the maintainer at the address on the GitHub profile, or open a
private security advisory via the repository's **Security** tab.

Include: a description, steps to reproduce, and the potential impact.

## Secrets

This project does **not** ship any API keys, tokens or credentials. Harvested
account data is written to `*.jsonl`, which is git-ignored. If you accidentally
commit credentials:

1. Revoke/rotate them immediately at the provider.
2. Remove the file from history (`git filter-repo` or BFG).
3. Force-push and inform the maintainer.

## Scope

Automating your own account creation and check-ins is the intended use.
Using this tool to mass-register accounts, evade rate limits, or attack the
service is out of scope and unsupported.
