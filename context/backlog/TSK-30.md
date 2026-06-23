# TSK-30: Refactor God Class CLIController to Adhere to SRP

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 4 Hours  
* **Story / Epic Reference:** FT-10 / REFACTOR  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

The current `CLIController` in `src/infra/cli.py` violates the Single Responsibility Principle (SRP) by handling CLI parsing, interactive shell loops, SMTP network requests, and HTML/CSV file exporting. This task refactors `CLIController` to segregate concerns into dedicated interfaces (ports) and adapters:
1. Extract interactive shell loop logic to `src/infra/shell.py`.
2. Extract SMTP email notification logic behind a new port `src/app/ports.py` (`INotificationService`) and its concrete adapter `src/infra/smtp_adapter.py`.
3. Extract HTML/CSV serialization and file system writing logic behind a new port `src/app/ports.py` (`IReportExporter`) and its concrete adapter `src/infra/exporters.py`.
4. Keep `cli.py` strictly focused on argparse command parsing and routing.

## ✅ Definition of Ready (DoR)

* [x] Basic CLI controller fully functioning (TSK-09).
* [x] Notifications, history, and report export features are already implemented (TSK-13, TSK-18, TSK-20).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **[Testing/Quality - TDD]:** Unit and integration tests are updated or created to validate the SMTP adapter, shell loop, and exporters independently.
* [x] **[Refactor - Domain/App]:** Interfaces `INotificationService` and `IReportExporter` are added to ports.
* [x] **[Refactor - Adapters]:** Implement `smtp_adapter.py`, `exporters.py`, and `shell.py` inside `src/infra/`.
* [x] **[Refactor - CLI]:** Clean up `cli.py` to route requests, reducing it to under 300 lines of code.
* [x] **[Verification]:** Full test suite runs and passes green with zero regressions.
