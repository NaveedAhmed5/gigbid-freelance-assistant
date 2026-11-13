from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
WEB_DIR = ROOT_DIR / "apps" / "web"

REQUIRED_SCREENS = [
    "src/app/onboarding/page.tsx",
    "src/app/inbox/page.tsx",
    "src/app/jobs/[id]/page.tsx",
    "src/app/studio/[id]/page.tsx",
    "src/app/pipeline/page.tsx",
    "src/app/messages/page.tsx",
    "src/app/runs/[id]/page.tsx",
    "src/app/analytics/page.tsx",
    "src/app/settings/page.tsx",
]

REQUIRED_COMPONENTS = [
    "src/components/Navbar.tsx",
    "src/components/DegradedModeBanner.tsx",
    "src/components/RequirementEvidenceMatrix.tsx",
    "src/components/ProposalStudioEditor.tsx",
    "src/components/DagViewer.tsx",
    "src/components/KanbanBoard.tsx",
]

REQUIRED_E2E_SPECS = [
    "tests/e2e/test_01_onboarding.spec.ts",
    "tests/e2e/test_02_proposal_approval.spec.ts",
    "tests/e2e/test_03_proposal_rejection.spec.ts",
    "tests/e2e/test_04_proposal_edit_memory.spec.ts",
    "tests/e2e/test_05_degraded_mode.spec.ts",
]


def test_all_9_frontend_screens_exist():
    for screen in REQUIRED_SCREENS:
        target = WEB_DIR / screen
        assert target.exists(), f"Frontend screen missing: {screen}"
        assert len(target.read_text(encoding="utf-8")) > 100


def test_all_frontend_components_exist():
    for comp in REQUIRED_COMPONENTS:
        target = WEB_DIR / comp
        assert target.exists(), f"Frontend component missing: {comp}"


def test_all_playwright_e2e_specs_exist():
    for spec in REQUIRED_E2E_SPECS:
        target = WEB_DIR / spec
        assert target.exists(), f"Playwright E2E spec missing: {spec}"


def test_typescript_api_client_exists():
    client_file = WEB_DIR / "src" / "lib" / "api" / "client.ts"
    assert client_file.exists()
    content = client_file.read_text(encoding="utf-8")
    assert "class GigBidClient" in content
    assert "submitApprovalDecision" in content

