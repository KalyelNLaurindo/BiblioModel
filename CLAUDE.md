# BiblioModel — Claude Code Reference Guide

This file provides system context, build/test commands, architecture guidelines, and coding standards for **BiblioModel** (an offline, local-first Python CLI library loan tracking and business rules engine).

---

## 🛠️ Common Commands

### Running the CLI
Run the main entry point via:
```bash
python src/main.py [command] [args]
```

### Running Tests
BiblioModel uses `pytest` for testing.
* **Run all tests:**
  ```bash
  pytest
  ```
* **Run with coverage report:**
  ```bash
  pytest --cov=src tests/
  ```
* **Run a specific test file:**
  ```bash
  pytest tests/test_domain.py
  ```

---

## 🏛️ Technology Stack & Constraints

- **Runtime Environment:** Pure Python 3.10+ (Standard Library only).
- **Dependencies:** **ZERO external third-party production dependencies**. Do NOT import or install external packages in `src/` (no SQLAlchemy, no Typer, no Pydantic). `pytest` is permitted only as a development dependency for executing the test suite.
- **Persistence:** In-Memory dynamic dictionaries serialized atomically to a local JSON file (`db_backup.json`), backed up as `db_backup.json.bak` on save.
- **Performance Target:** All memory-resident searches, lookups, and state mutations must maintain $O(1)$ complexity and run in under 10 milliseconds.

---

## 🏗️ Architectural Guardrails (Hexagonal & DDD)

Code must follow strict Hexagonal Architecture / Clean Architecture principles:

1. **Domain Isolation:** Code inside `src/domain/` must remain completely pure. It cannot import from `infra`, `cli`, `app`, or use cases.
2. **Ports & Adapters (DIP):** Interactivity with filesystem, config, and terminal shell must happen strictly through adapters. Use cases must only depend on abstract interface declarations (Ports) e.g., `ILibraryRepository`.
3. **Data Durability:** All database mutator actions must run through the atomic write service: serialize to `.tmp` first, then execute `os.replace()` to replace the target `.json` file to avoid corruption.
4. **FIFO Hold Queues:** Popular books must use a first-in-first-out (FIFO) queue for managing reservations, blocking standard checkouts when a reservation is active.
5. **Engineering Principles:** Always design and write code following Object-Oriented Programming (OOP), Domain-Driven Design (DDD), DRY, KISS, SOLID principles, Design Patterns, and Clean Code standards.

---

## 🧪 Testing Paradigm (TDD Mandatory)

- **Strict Order:** Write and deliver the corresponding `pytest` file (under `tests/`) **BEFORE** implementing the production classes. Any production code without preceding tests will be rejected.
- **Boundary Conditions:** Implement explicit tests checking boundary conditions (e.g., negative loan durations, invalid reader IDs, past due dates, fine waiver conditions).

---

## 📂 Codebase Directory Structure

```text
BiblioModel/
├── src/                          # System codebase root directory  
│   ├── domain/                   # Bounded domain context (entities, value objects, ports)  
│   │   ├── __init__.py  
│   │   ├── entities.py           # BookEntity, ReaderEntity, LoanEntity classes  
│   │   └── services.py           # FineCalculator rule engine  
│   │  
│   ├── app/                      # Application layer (business use cases)  
│   │   ├── __init__.py  
│   │   ├── ports.py              # Outbound interface ports (ILibraryRepository)  
│   │   └── use_cases.py          # CheckoutUseCase, ReturnUseCase, ReserveUseCase  
│   │  
│   ├── infra/                    # Adaption layer (file systems, terminal integrations)  
│   │   ├── __init__.py  
│   │   ├── adapters.py           # JSONPersistenceAdapter, INIConfigAdapter  
│   │   └── cli.py                # argparse CLI controller implementation  
│   │  
│   └── main.py                   # Unified CLI application entrypoint bootstrap  
├── tests/                        # Validation suite directory  
│   ├── __init__.py  
│   ├── test_domain.py            # Unit tests validating rules and domain entities  
│   ├── test_use_cases.py         # Integration tests validating use case flows  
│   └── test_persistence.py       # Persistence tests (atomic writes & self-healing)  
├── pyproject.toml                # Standard setuptools configuration file  
├── config.ini                    # Core parameter configurations (fine daily rates, limits)  
└── README.md                     # Initial setup instructions and documentation
```

---

## 🏷️ Code Governance & Naming Conventions

Maintain strict compliance with PEP 8 and the following conventions:

*   **Language & Style:** All inline code comments and code docstrings must be written in English. However, **all implementation plans (`implementation_plan.md`), walkthroughs (`walkthrough.md`), and user-facing design explanations must be written in Portuguese (PT-BR)**, using clear, simple, and highly explanatory language so that any developer or stakeholder can easily understand the proposed changes.
*   **Suffixes & Prefixes:**

| Role / Pattern | Suffix / Prefix | Example Name |
| :--- | :--- | :--- |
| **Domain Entity** | `Entity` suffix | `BookEntity` |
| **Value Object** | `ValueObject` suffix | `FineValueObject` |
| **Application Action** | `UseCase` suffix | `CheckoutUseCase` |
| **Storage Port Interface** | `I` prefix | `ILibraryRepository` |
| **Concrete Adapter** | `Adapter` suffix | `JSONPersistenceAdapter` |
| **Console Command Router**| `Controller` suffix | `CLIController` |

---

## 🌿 Git Workflow & Commit Conventions

*   **Branching Strategy:**
    *   All development must take place on feature branches (e.g., `feature` or `feature/TSK-XX-description`).
    *   **CRITICAL REQUIREMENT:** A separate git feature branch must be used for each phase of the project implementation (e.g., `feature/phase-0-bootstrap`, `feature/phase-1-infrastructure`, `feature/phase-2-domain`, `feature/phase-3-usecases`, etc.) to keep delivery phases isolated and tidy.
    *   Direct commits to the main integration branch (`main`/`develop`) are prohibited; code must be merged via Pull Requests.
*   **Semantic Commit Messages:** Use conventional commit formatting to describe changes clearly:
    *   `feat(scope):` Introduces a new feature or domain component (e.g., `feat(domain): add FIFO hold queue to BookEntity`).
    *   `fix(scope):` Patches a software bug or corrects an active system failure.
    *   `docs(scope):` Updates markdown documents, guides, changelogs, or walkthroughs.
    *   `test(scope):` Adds or updates test files without changing production code.
    *   `chore(scope):` Builds setups, git configurations, or project bootstrapping actions.

---

## 📋 Planning & Execution Flow Checklist

For every task, the AI agent and developer must strictly follow this lifecycle:

1.  **Planning Phase (Before Code Modifications):**
    *   Create `implementation_plan.md` in the current conversation directory (written in Portuguese, PT-BR).
    *   Mark `request_feedback = true` in the plan metadata.
    *   **STOP** and wait for the user's explicit approval before writing any code.
2.  **Execution Phase (TDD Protocol):**
    *   Create/update `task.md` in the conversation directory to track checklist items using `[ ]` (pending), `[/]` (in progress), and `[x]` (completed).
    *   Write corresponding test cases under `tests/` **BEFORE** implementing production code. Run pytest to assert they fail.
    *   Implement domain logic in `src/` to satisfy the tests.
    *   Run all tests with `pytest` to achieve 100% pass rate.
3.  **Completion & Delivery Phase:**
    *   Mark all **Definition of Ready (DoR)** and **Definition of Done (DoD)** checkboxes as completed (`[x]`) inside the task's individual markdown file (`context/backlog/TSK-XX.md`).
    *   Update the Kanban board and the task status to `Done` in the backlog master file (`context/backlog/README.md`).
    *   Create `walkthrough.md` in the conversation directory summarizing changes (written in Portuguese, PT-BR).
    *   Stage and commit modified files using Conventional Commits naming standards (e.g., `feat(domain): ...`, `docs(backlog): ...`).

