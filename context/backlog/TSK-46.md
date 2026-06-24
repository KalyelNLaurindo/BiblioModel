# TSK-46: Terminal UI/UX Overhaul — Interactive Shell Visual Redesign

* **Owner / Assignee:** Kalyel Nunes Laurindo / PO  
* **Estimated Effort:** 3 Hours  
* **Story / Epic Reference:** Phase 13 / UX Terminal  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

The current interactive shell (`bibliomodel shell`) is functional but visually raw. It lacks a branded welcome banner, visual hierarchy in output tables, consistent icon/color feedback conventions, and visual separation between command cycles. This task performs a full visual redesign of the interactive shell experience without breaking any existing functionality or the i18n layer.

### Pain Points Identified (User Reported)

1. **No welcome screen / banner** — The shell launches into a bare prompt with no context about the system name, version, or commands.
2. **Unformatted output tables** — Loan listings, reservation status, and reader search results are plain text with no visual structure.
3. **Inconsistent feedback** — Success, warning, and error messages have no consistent color/icon convention across commands.
4. **No visual separation between commands** — Each command's output blends visually into the next REPL cycle.
5. **Unpolished prompt** — The shell prompt lacks color or visual affordance.

### Deliverables

1. **Branded ASCII banner** displayed once on shell startup — application name ("BiblioModel"), version, tagline ("Library Management Engine"), and a hint to type `help`.
2. **Color-coded prompt** — `bibliomodel ❯` in cyan, with user input in default terminal color.
3. **Consistent message icons** — `✅` success, `⚠️` warning, `❌` error, `ℹ️` info — prepended to all feedback lines across all shell commands.
4. **Boxed output sections** — Loan/reservation/reader tables wrapped in light Unicode box borders (`╭`, `─`, `│`, `╰`) with aligned columns.
5. **Separator lines** — Thin `─` dividers printed between consecutive command output cycles in the REPL.
6. **i18n-aware rendering** — All new visual strings (banner tagline, icon labels) must pass through the `TranslationService` to remain localized.
7. **Graceful degradation** — All enhancements behind a `supports_unicode()` check; plain ASCII fallback for restricted terminals and `NO_COLOR=1` env.

## ✅ Definition of Ready (DoR)

* [x] Interactive shell (`bibliomodel shell`) is implemented and functional.
* [x] `TranslationService` i18n layer is available for all output strings (TSK-32/33/34).
* [x] `rich` or `colorama` is available in the dependency stack.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **[Functional - Banner]:** Launching `bibliomodel.exe` or `bibliomodel shell` displays a branded ASCII banner with name, version, and tagline (localized via i18n).
* [ ] **[Functional - Prompt]:** The REPL prompt renders as a colored `bibliomodel ❯` with user input in default terminal color.
* [ ] **[Functional - Feedback Icons]:** All success/error/warning/info outputs consistently prepend the appropriate icon across every command (`loan`, `return`, `reserve`, `reader`, `search`, etc.).
* [ ] **[Functional - Tables]:** Loan listings, reservations, and reader records render inside Unicode box borders with aligned columns.
* [ ] **[Functional - Separators]:** A thin `─` divider is printed after each command output in the REPL cycle.
* [ ] **[Functional - i18n]:** Banner tagline and all new UI strings are registered as translation keys and rendered through `TranslationService`.
* [ ] **[Functional - Fallback]:** `NO_COLOR=1` or `--no-color` strips ANSI codes and replaces Unicode box chars with plain ASCII equivalents.
* [ ] **[Testing/Quality - TDD]:** Visual rendering helpers are unit-tested via `capsys` stdout capture, asserting icon, border, and divider presence per locale and per color-mode scenario.
* [ ] **[Verification]:** Full test suite (`pytest`) runs with 100% pass rate (no regressions).
