# TSK-15: Implement Interactive CLI Prompt Shell

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-05 (CLI & Alerts Router)

## 📖 Description & Objectives

Construct an interactive console prompt shell inside `src/infra/cli.py` (e.g., executing when calling `bibliomodel shell`). Instead of exiting immediately after a single command runs, the application starts a persistent command loop allowing librarians to run successive checkout, return, and lookup operations without rebooting the Python process.

## ✅ Definition of Ready (DoR)

* [ ] CLI Argument Router (`TSK-09`) is functional.
* [ ] State persistence and use case operations are verified.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Functional):** Operator enters a persistent prompt loop, executing operations and receiving outputs. Typing `exit` or `quit` gracefully terminates the process.
* [ ] **Criterion 2 (Quality/Test):** Shell loop captures interrupts (Ctrl+C, Ctrl+D) and terminates without throwing raw tracebacks.
* [ ] **Criterion 3 (Security/Resilience):** Saves active memory states to `db_backup.json` automatically on each action within the shell loop.
* [ ] **Criterion 4 (Review):** Standard library only (built using standard Python input loops and `cmd` module or simple loops).
