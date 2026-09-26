# Week 5 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (?) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: Fibbin \
SUNet ID: Null \
Citations: **Warp Documentation (https://docs.warp.dev/), SQLAlchemy 2.0 Documentation, FastAPI Testing Documentation, and Google Gemini Flash via Warp BYO-LLM.**

This assignment took me about **3** hours to do. 


## YOUR RESPONSES
### Automation A: Warp Drive saved prompts, rules, MCP servers

a. Design of each automation, including goals, inputs/outputs, steps
> - **Goal**: Provide a single-command, idempotent verification pipeline on Windows PowerShell where the repository's `Makefile` targets (`make test`, `make lint`, `make format`) do not run natively without GNU Make, and automatically resolve module path (`PYTHONPATH`) or formatting issues.
> - **Artifact Location**: Saved in Warp Drive as a Prompt (`Week5 Windows Check & Test Runner`) and exported to `.warp/workflows/windows_check_test.yaml` and `.warp/multi_agent_playbook.md`.
> - **Inputs / Outputs**: Takes the current working directory (`week5/`) as context; outputs `pytest` pass/fail summaries, `ruff` lint diagnostics, and `black` formatting status.
> - **Steps**:
>   1. Execute `python -m pytest -q backend/tests` (using `python -m` so the root `week5/` directory is added to `sys.path` on Windows).
>   2. Run `ruff check .` to catch unused imports or style violations.
>   3. Run `black --check .` to verify code formatting compliance.
>   4. If any step fails, the agent parses the traceback or linter output and applies targeted fixes automatically.

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> - **Before (Manual Workflow)**: Running `make test` on Windows failed because `make` is not installed by default in PowerShell. Running `pytest -q backend/tests` directly also threw `ModuleNotFoundError: No module named 'backend'` because the current working directory was not in `sys.path`. I had to manually type out separate commands for `python -m pytest`, `ruff`, and `black` after every code change.
> - **After (Automated Workflow)**: Triggering the Warp Drive prompt/workflow executes the entire test + lint + format verification suite in one headless step and automatically diagnoses environment or import-path errors.

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> - **Permissions**: File read access across `week5/`, file write access restricted to `backend/` and `.warp/`, and command execution permission for non-destructive test/lint commands (`python -m pytest`, `ruff`, `black`).
> - **Why & Supervision**: Allowing autonomous execution of read-only test and linter commands eliminated repetitive manual confirmation prompts while keeping file modifications supervised via Warp's command/diff review UI.

d. (if applicable) Multi?agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> - Used this Warp Drive check runner as the final post-merge verification gate after both task agents completed their changes on `models.py` and `backend/tests/`.

e. How you used the automation (what pain point it resolves or accelerates)
> - It resolved two immediate pain points on Windows: the lack of native `Makefile` support in PowerShell and the `ModuleNotFoundError` during `pytest` discovery. It accelerated verification after implementing Tasks 9 and 10 from ~2 minutes of manual command typing to a single 3-second run.



### Automation B: Multi?agent workflows in Warp 

a. Design of each automation, including goals, inputs/outputs, steps
> - **Selected Tasks**:
>   1. **Task 9: Query performance and indexes (Difficulty: easy?medium)** ? Add SQLite indexes on frequently queried columns (`notes.title` and `action_items.completed` in `backend/app/models.py`) and verify query plans (`EXPLAIN QUERY PLAN`) and performance using a 120-row seeded dataset.
>   2. **Task 10: Test coverage improvements (Difficulty: easy)** ? Expand `backend/tests/` to cover 404 Not Found responses, 400/422 payload validation errors, database session transactional rollbacks on mid-transaction exceptions, and sequential bulk operation consistency.
> - **Inputs / Outputs**: Scoped prompts (documented in `.warp/multi_agent_playbook.md`) restricting each agent to specific files; outputs updated SQLAlchemy models and comprehensive pytest suites.
> - **Steps**:
>   1. Configure Warp Agent in Tab 1 to implement Task 9 (`backend/app/models.py` and index/query-plan tests in `backend/tests/test_notes.py`).
>   2. Configure Warp Agent in Tab 2 to implement Task 10 (error/rollback/bulk coverage in `backend/tests/test_action_items.py` and `backend/tests/test_notes.py`).
>   3. Run the unified test and linter suite to confirm zero regressions.

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> - **Before (Sequential Manual Workflow)**: Implementing schema index changes, writing SQLite `PRAGMA index_list` / `EXPLAIN QUERY PLAN` assertions, and writing edge-case tests for every router endpoint had to be done sequentially one file at a time.
> - **After (Concurrent Multi-Agent Workflow)**: By partitioning the tasks by file ownership across two Warp tabs, schema indexing (Task 9) and endpoint/transaction test coverage (Task 10) were developed in parallel.

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> - **Task 9 (easy?medium)**: Medium autonomy ? the agent was permitted to read and modify `backend/app/models.py` and `backend/tests/test_notes.py` and run `pytest` autonomously, while I reviewed the schema diff to ensure no breaking changes to existing columns.
> - **Task 10 (easy)**: High autonomy ? strictly scoped to `backend/tests/` with an explicit constraint (`Do not modify models.py`), making it safe to let the agent generate and run test cases autonomously.

d. (if applicable) Multi?agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> - **Roles**: Agent 1 acted as the *Database & Performance Engineer* (Task 9); Agent 2 acted as the *QA & Reliability Engineer* (Task 10).
> - **Coordination Strategy**: Strict file-level scoping in the prompts prevented write collisions (`models.py` owned exclusively by Agent 1; `test_action_items.py` owned by Agent 2).
> - **Concurrency Wins, Risks & Failures**:
>   - *Win*: Zero Git merge conflicts because file boundaries were explicitly defined in the prompts.
>   - *Failure / Risk Encountered*: When running multiple agents simultaneously using a free-tier BYO Google Gemini API key, Default `gemini-3.1-pro` hit a 0-quota 429 error, and un-scoped prompts on `gemini-flash` quickly exhausted the 250,000 input tokens/minute rate limit.
>   - *Mitigation*: Switched the model to Gemini Flash, staggered agent start times, and constrained each prompt to read only the target files (`models.py`, `routers/`, `tests/`) instead of scanning the entire repository.

e. How you used the automation (what pain point it resolves or accelerates)
> - Multi-agent execution accelerated delivering both Task 9 and Task 10 within a single session while ensuring that new SQLite indexes (`ix_notes_title`, `ix_action_items_completed`) and 100% of endpoint 404/422 error paths and transaction rollbacks were verified by automated tests.
