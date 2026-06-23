# TSK-34: Interactive Localized Shell UX & Error Badges

* **Owner / Assignee:** Kalyel Nunes Laurindo / Tech Lead  
* **Estimated Effort:** 2 Hours  
* **Story / Epic Reference:** FT-10 / i18n UX  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Improve CLI console usability for non-technical librarians by adding simple language selector dialogs, persistent status lines, and visual help improvements.

Tasks:
1. Provide a language selection command/prompt menu inside `shell.py` using single characters `[1-5]`.
2. Add a persistent terminal header showing operational status: `[Language: EN | DB: OK | Active Overdues: 0]`.
3. Standardize error alerts using color-coded Unicode brackets `[WARN]`, `[ERROR]`, `[SUCCESS]`.

## ✅ Definition of Ready (DoR)

* [x] i18n Presenter Localization adapter is functional (TSK-33).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **[Functional - Interactive]:** Dynamic switching of active language during a running interactive shell session is possible.
* [x] **[Functional - Shell]:** Interactive prompt shows shortcut actions in the active language (e.g. `[L] Switch Language | [Q] Quit`).
* [x] **[Functional - Resiliency]:** Reverts table borders and alert icons to ASCII-only format if terminal configuration cannot parse Unicode.
* [x] **[Verification]:** `pytest` tests pass 100% green.
