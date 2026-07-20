# Publishing this repo to GitHub (read via link, no public edit)

GitHub does **not** offer Google-Drive-style “anyone with the link can view but not edit” on a **private** repo. Closest options:

| Goal | Setup |
|------|--------|
| **Anyone with the URL can read/clone; only you (and invited writers) can push** | **Public** repository (recommended for “link = read only”). |
| **Named people only, read-only** | **Private** repo → **Settings → Collaborators** → invite with role **Read**. No anonymous link. |

**Editing the code on GitHub** always requires **Write** (or higher) on the repo. Public visitors can still open Issues/PRs unless you change settings; they cannot push to `main` unless they have write access.

## One-time setup

1. **Revoke any token that was pasted in chat** and create a new one:  
   [GitHub → Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)

2. **Token permissions** (pick one style):
   - **Classic:** enable scope **`repo`** (full control of private repositories; includes create + push).
   - **Fine-grained:** for your user or this repo — **Contents: Read and write**, **Metadata: Read**, and **Administration: Read and write** if you want API repo creation.

3. **Create the empty repo** (browser):  
   [https://github.com/new](https://github.com/new)  
   - Owner: `ppuregoldz-arch` (or your org)  
   - Name: `slotomania-mm-calendar`  
   - Visibility: **Public** (for link read access)  
   - Do **not** add README, `.gitignore`, or license (this project already has them).

4. **Push from this folder** (token is the password when Git asks; username is your GitHub login):

```bash
cd "/Users/itayg/Desktop/Cursor Work"
git remote add origin https://github.com/ppuregoldz-arch/slotomania-mm-calendar.git
git branch -M main
git push -u origin main
```

Or use the helper (after `export GITHUB_TOKEN='…'` with a **new** token):

```bash
export GITHUB_TOKEN='YOUR_NEW_TOKEN'
python3 scripts/github_push_origin.py
unset GITHUB_TOKEN
```

## Required department hardening

Repository files now provide `.github/CODEOWNERS`, a Pull Request template, a tool-improvement Issue form, and the `Department tooling smoke` workflow.

Configure **Settings → Rules → Rulesets** for `main`:

- require a Pull Request;
- require at least one approval;
- require CODEOWNERS review;
- require the `Department tooling smoke / validate` status check;
- block force pushes and branch deletion;
- restrict direct pushes to the repository owner/maintainers.

Keep Issues enabled so department members can submit Tool improvement forms. Never commit `.cursor/monday.env`, `.cursor/mcp.json`, or other secrets.

## Local vs team canonical copy

Team studio path remains in `BACKUP_LOCAL.md` and `AGENTS.md`. GitHub is an additional read/share copy, not a replacement for the CRM volume.
