# AGENTS.md: SurvivalChurn Matrix Operating Manual

## 1. Project Overview & Core Mission
**SurvivalChurn Matrix** is a high-performance predictive analytics engine designed to model customer attrition using survival analysis (Cox Proportional Hazards, Kaplan-Meier estimators) and stochastic matrix transitions. 

**Core Mission:** To provide a deterministic, production-ready framework for churn forecasting that prioritizes mathematical rigor, memory efficiency, and zero-copy data processing. Agents must maintain the integrity of the underlying statistical models while ensuring the codebase remains decoupled from specific data ingestion layers.

## 2. Local PowerShell Commands
All automation must be executed via the project root. Agents are required to verify the environment before execution.

*   **Setup:** `.\scripts\init.ps1` (Installs `poetry` dependencies, configures pre-commit hooks, and validates `python 3.11+` path).
*   **Test:** `pytest tests/ --cov=src --cov-report=term-missing --durations=10`
*   **Run:** `python -m src.main --config ./configs/prod.yaml`
*   **Lint:** `ruff check . && mypy src/ --strict`
*   **Format:** `black . && isort .`

## 3. Engineering Invariants
*   **Zero-Placeholder Mandate:** No `TODO`, `FIXME`, or `pass` blocks allowed in production code. If a feature is incomplete, it must be explicitly raised as `NotImplementedError` with a tracking issue ID.
*   **Typing Strictness:** All functions must include full type hints. Use `typing.Protocol` for dependency injection. `Any` is strictly forbidden unless explicitly justified in a comment block.
*   **CRLF/LF Preservation:** The repository enforces `LF` line endings. Agents must ensure `.gitattributes` is respected; no mixed line endings allowed.
*   **Memory Safety:** Large datasets must be processed via `numpy` memory mapping or `polars` lazy frames. No loading full datasets into native Python lists.
*   **Decoupling:** Business logic must reside in `src/core/`. Data IO must reside in `src/io/`. No cross-contamination.

## 4. Self-Healing & Error Recovery Protocol
When an agent encounters a traceback or runtime failure, it must execute the following protocol:

1.  **Traceback Isolation:** Capture the full stack trace. If the error occurs in a statistical module, isolate the input vector using the `tests/reproducers/` directory.
2.  **State Inspection:** Run `python -m src.debug.inspect_state --last-run` to dump the internal matrix state at the point of failure.
3.  **Hypothesis Testing:** Before applying a fix, create a minimal unit test in `tests/unit/` that triggers the specific failure.
4.  **Verification:** Apply the fix, run the specific unit test, then run the full suite.
5.  **Regression Check:** If the fix modifies a mathematical core, verify against the `tests/benchmarks/` to ensure no performance degradation (max 2% latency increase allowed).

## 5. Definition of Done (DoD) Quality Gate
A task is only "Done" when the following criteria are met:

*   **Coverage:** 95%+ branch coverage verified by `pytest-cov`.
*   **Static Analysis:** Zero errors reported by `mypy --strict` and `ruff`.
*   **Documentation:** All public methods/classes have `Google-style` docstrings including `Args`, `Returns`, and `Raises` sections.
*   **Performance:** Execution time for the `SurvivalMatrix` calculation is within the 95th percentile of the baseline benchmark.
*   **Integration:** The change passes the full CI pipeline (GitHub Actions) including cross-platform compatibility checks.
*   **Cleanliness:** No orphaned imports, no unused variables, and no commented-out code blocks.