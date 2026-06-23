# TSK-35: Library CLI A11y Suite (Monochrome high-contrast themes and clean reader streams)

* **Owner / Assignee:** Kalyel Nunes Laurindo / Tech Lead  
* **Estimated Effort:** 2 Hours  
* **Story / Epic Reference:** FT-10 / Acessibilidade  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Enforce accessibility compliance in BiblioModel's command-line interface, ensuring screen readers (NVDA/JAWS) and non-standard shell terminals process printed output without visual fragmentation.

Tasks:
1. Support standard environment variable `NO_COLOR` and `--no-color` parameter to completely bypass ANSI styling escapes.
2. Structure list layouts (`list-books`, `list-readers`) to output as clean, non-nested text blocks when `--linear` is executed, preventing screen readers from wrapping columns out of order.
3. Validate typography contrast of the CLI.

## ✅ Definition of Ready (DoR)

* [x] Presentation adapters localization is completed (TSK-33).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **[Testing/Quality - TDD]:** Test cases assert that calling shell commands with environment `NO_COLOR=1` or parameter `--no-color` outputs clean plain-text strings with no escape sequences.
* [x] **[Functional - Accessibility]:** CLI implements parameter `--linear` which strips borders and columns, outputting a top-to-bottom list of properties.
* [x] **[Functional - Visuals]:** Validation errors translate to clear text banners (e.g. `[ERROR]`) instead of relying solely on red foreground colors.
* [x] **[Verification]:** pytest runs successfully with 100% pass rate.
