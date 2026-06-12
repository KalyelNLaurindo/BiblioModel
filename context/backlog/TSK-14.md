# TSK-14: Implement Semi-Visual Terminal Table Renderer and Welcome Interface

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-05 (CLI & Alerts Router)

## 📖 Description & Objectives

Construct a custom console utility to render data outputs (such as book lists, active loans, and reader summaries) in clean ASCII/Unicode text-box frames ("com traços"). The system must draw clean structural boxes and table grids using box-drawing characters (e.g. `┌`, `─`, `┬`, `┐`, `│`, `├`, `┼`, `┤`, `└`, `┴`, `┘`) instead of standard plain comma-spaced text. Additionally, build a formatted welcome banner displaying when the CLI boots.

## ✅ Definition of Ready (DoR)

* [x] CLI Argument Router (`TSK-09`) is functional.
* [x] Database read adapters and domain entity collections are ready.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **Criterion 1 (Functional):** The CLI outputs tables (e.g., when calling `bibliomodel list-books` or `bibliomodel report`) wrapped in clean boxes made of single-line or double-line box-drawing characters, maintaining correct column alignment for varying text sizes.
* [x] **Criterion 2 (Quality/Test):** Unit tests located in `tests/test_use_cases.py` (or test_infra.py) verify that formatting functions return correct string lengths and boundary paddings.
* [x] **Criterion 3 (Security/Resilience):** Handles long string inputs (such as very long book titles) by trimming or wrapping text to prevent table boundaries from breaking.
* [x] **Criterion 4 (Review):** Standard library only (zero external libraries like `tabulate` or `rich`). Written entirely in pure Python.

