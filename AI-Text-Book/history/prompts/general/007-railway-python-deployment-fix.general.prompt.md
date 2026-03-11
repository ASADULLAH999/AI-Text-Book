---
id: 007
title: Railway Python Deployment Fix
stage: general
date: 2026-03-11
surface: agent
model: claude-sonnet-4-6
feature: none
branch: master
user: ASADULLAH999
command: fix railway deployment for FastAPI
labels: ["deployment", "railway", "fastapi", "python", "devops"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - nixpacks.toml
  - railway.json
  - runtime.txt
  - Procfile
tests:
  - none
---

## Prompt

I am deploying my FastAPI project on Railway and the deployment is failing during the build process.

Error message:
pip install -r requirements.txt
sh: 1: pip: not found
process "sh -c pip install -r requirements.txt" did not complete successfully: exit code: 127

Railway seems to be detecting the project as a Node.js project instead of a Python FastAPI project.

Please fix the repository so Railway correctly detects it as a Python project.
Make the necessary changes such as:
* Ensure the correct Python runtime is specified.
* Add or fix runtime.txt if needed.
* Verify requirements.txt is correct.
* Ensure the FastAPI app start command works (uvicorn or hypercorn).
* Make sure the project structure is compatible with Railway deployment.

## Response snapshot

Root cause: Railway detects root-level `package.json` (Docusaurus/Node.js) and ignores the Python FastAPI app in `api/` subdirectory. The `Procfile` and `requirements.txt` were only inside `api/`, invisible to Railway's root-level scan.

Created 4 files at the repo root:
1. `nixpacks.toml` — forces `python` provider, overrides Node detection, installs from `api/requirements.txt`, starts with `cd api && uvicorn src.main:app`
2. `railway.json` — Railway-specific config with explicit buildCommand and startCommand
3. `runtime.txt` — specifies `python-3.11`
4. `Procfile` — root-level fallback: `web: cd api && uvicorn src.main:app --host 0.0.0.0 --port $PORT`

## Outcome

- ✅ Impact: Railway will now correctly detect Python runtime and deploy the FastAPI app from the `api/` subdirectory
- 🧪 Tests: No automated tests; manual Railway deploy required to verify
- 📁 Files: nixpacks.toml, railway.json, runtime.txt, Procfile (all at repo root)
- 🔁 Next prompts: commit and push changes, redeploy on Railway
- 🧠 Reflection: Monorepo with mixed Node.js + Python requires explicit nixpacks/railway config to override auto-detection

## Evaluation notes (flywheel)

- Failure modes observed: Railway auto-detection prioritizes package.json over requirements.txt when both exist
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment: if build still fails, try moving requirements.txt to root or using Railway's "Root Directory" setting in dashboard to point at `api/`
