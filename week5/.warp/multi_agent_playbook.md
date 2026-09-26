# Week 5 Multi-Agent Playbook & Saved Prompts

## 1. Warp Drive Saved Prompt
**Name**: `Week5 Windows Check & Test Runner`
**Prompt**:
> Run the test suite and linters for the week5 FastAPI project on Windows. Execute `python -m pytest -q backend/tests`, `ruff check .`, and `black --check .` inside the `week5` directory. If any tests fail or lint/format checks report issues, analyze the output and fix them automatically.

## 2. Multi-Agent Coordination Prompts
- **Agent 1 (Tab 1 - Task 9: Query Performance & Indexes)**:
  > Implement Task 9: Only read and modify `backend/app/models.py` to add `index=True` on beneficial columns (`Note.title`, `ActionItem.completed`), and add a test in `backend/tests/test_notes.py` to verify query plans/performance with a seeded dataset. Run `python -m pytest -q backend/tests` to verify.
- **Agent 2 (Tab 2 - Task 10: Test Coverage Improvements)**:
  > Implement Task 10: Only read `backend/app/routers/` and `backend/tests/`. Add unit tests covering 400/422/404 error scenarios for endpoints and transactional rollback behavior. Do not modify `models.py`. Run `python -m pytest -q backend/tests` to verify.
