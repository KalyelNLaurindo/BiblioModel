# TSK-32: i18n Core Translation Service & Registry

* **Owner / Assignee:** Kalyel Nunes Laurindo / Tech Lead  
* **Estimated Effort:** 3 Hours  
* **Story / Epic Reference:** FT-10 / i18n Core  
* **Development Methodology:** TDD (Red-Green-Refactor)

## 📖 Description & Objectives

Design and implement a zero-dependency translation core service for BiblioModel that registers and resolves UI string resources in Portuguese, English, French, Spanish, and German.

The core service will:
1. Parse JSON files representing each locale under `locales/` directory.
2. Read system settings from `config.ini` to resolve default locale (e.g. `lang = en`).
3. Offer an outbound port `ITranslationService` and concrete adapter to load, cache, and fetch values with replacement tokens (e.g. `translate("fine_amount", amount=5.0)`).

## ✅ Definition of Ready (DoR)

* [x] Configuration Adapter `INIConfigAdapter` is fully operational (TSK-01).

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **[Testing/Quality - TDD]:** Test suite asserts that `ITranslationService` loads JSON profiles correctly and formats interpolation variables in all 5 target languages.
* [ ] **[Functional - Locales]:** Directory `locales/` contains valid resource files: `pt.json`, `en.json`, `fr.json`, `es.json`, `de.json`.
* [ ] **[Functional - Fallback]:** Resolves active language using hierarchy: 1. argparse `--lang` flag, 2. `config.ini` `lang` entry, 3. system environment locale, 4. default `pt`.
* [ ] **[Verification]:** `pytest` tests pass 100% green.
