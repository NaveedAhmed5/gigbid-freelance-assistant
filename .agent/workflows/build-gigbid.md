// turbo-all
# GigBid Build Workflow

This workflow executes and resumes the multi-phase autonomous execution for GigBid (AI-4016 R&D Assignment).

## Step 1: Check Current Progress
Check `PROGRESS.md` to identify the first unchecked phase `[ ] Phase X`.

## Step 2: Read Phase Specification
Read `scripts/phases/phase_0X_*.md` for the corresponding phase.

## Step 3: Implement Phase Code and Assets
Implement all required files, modules, configs, tests, and runners for the phase strictly adhering to `GEMINI.md`.

## Step 4: Verification
Execute unit tests, integration tests, or evaluation scripts via `pytest` or command line:
```powershell
pytest -q
```
Fix any syntax, import, or test failures immediately.

## Step 5: Mark Completed & Commit
1. Update `PROGRESS.md` marking the phase `[x]`.
2. Commit to git:
```powershell
git add .
git commit -m "Completed Phase X"
```

## Step 6: Loop
Repeat Steps 1-5 until all Phases 0 through 10 in `PROGRESS.md` are marked `[x]`.

