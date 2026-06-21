# **📋 Backlog: BiblioModel**

**Role:** Agile Coach / Tech Lead / Project Manager

**Objective:** Maintain a prioritizable backlog of atomic, SMART tasks, tracking their progress across a basic Markdown Kanban board from planning to verification.

**Context:** BiblioModel — A domain model and logic engine designed to enforce business rules, handle book loans, manage inventory states, and automate fine calculations for a mid-sized library experiencing asset loss and operational bottlenecks.

## **🏛️ Backlog Metadata**

* **Project Owner:** Kalyel Nunes Laurindo / PO  
* **Lead Tech Lead:** Kalyel Nunes Laurindo / Tech Lead  
* **Current Sprint / Iteration:** Sprint 1 (Infrastructure & Domain Foundations)  
* **Target Delivery Date:** July 15, 2026  
* **Document Version:** v1.0

---

## **1. 📊 Prioritization & Task Sizing Framework**

To keep development cycles efficient, tasks are estimated and prioritized before execution using the RICE framework.

### **1.1. RICE Score Calculation Formula**

RICE = (Reach * Impact * Confidence) / Effort

* **Reach:** Scaled from 1 to 100 based on the proportion of system layers or user touchpoints affected.  
* **Impact:** Qualitative contribution to the product vision (3 = Massive, 2 = High, 1 = Medium, 0.5 = Low).  
* **Confidence:** Certainty of estimates (1 = High/100%, 0.8 = Medium/80%, 0.5 = Low/50%).  
* **Effort:** Total developer-weeks or story points required (1 = Low, 5 = High).

---

## **2. 🗂️ Prioritized Product Backlog Ledger**

The backlog is structured in a strict TDD (Domain-Driven Bottom-Up) order, starting with pure domain logic and working outwards to infrastructure, CLI routing, and deployment.

### **📦 Phase 0: Project Bootstrap**

* **[[TSK-00](TSK-00.md)]: Bootstrap project workspace directory layout and initial validation configs**  
  * *Epic Link:* FT-01 (Bootstrap & Config Setup)  
  * *RICE Score:* 150.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  

### **📦 Phase 1: Infrastructure Foundations & Setup**

* **[[TSK-01](TSK-01.md)]: Implement Core Configuration Parser and Logging Setup**  
  * *Epic Link:* FT-01 (Bootstrap & Config Setup)  
  * *RICE Score:* 150.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  

### **⚙️ Phase 2: Pure Domain Layer (TDD Innermost Core)**

* **[[TSK-02](TSK-02.md)]: Build Domain Entity - BookEntity and FIFO Hold Queue**  
  * *Epic Link:* FT-02 (Bounded Domain Objects)  
  * *RICE Score:* 270.0 (High Priority / Must Have) | Reach: 90 / Impact: 3 / Confidence: 1.0 / Effort: 1  
  * *Status:* Done  
* **[[TSK-03](TSK-03.md)]: Build Domain Entities - ReaderEntity & LoanEntity**  
  * *Epic Link:* FT-02 (Bounded Domain Objects)  
  * *RICE Score:* 150.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  
* **[[TSK-04](TSK-04.md)]: Develop Domain Services - FineCalculator Engine**  
  * *Epic Link:* FT-02 (Bounded Domain Objects)  
  * *RICE Score:* 120.0 (High Priority / Must Have) | Reach: 80 / Impact: 3 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  

### **🧠 Phase 3: Application Use Cases (In-Memory Orchestration)**

* **[[TSK-05](TSK-05.md)]: Create Application Use Case - CheckoutUseCase**  
  * *Epic Link:* FT-03 (Use Case Interactors)  
  * *RICE Score:* 100.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* Done  
* **[[TSK-06](TSK-06.md)]: Create Application Use Case - ReturnUseCase**  
  * *Epic Link:* FT-03 (Use Case Interactors)  
  * *RICE Score:* 100.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* Done  
* **[[TSK-07](TSK-07.md)]: Create Application Use Case - ReserveUseCase**  
  * *Epic Link:* FT-03 (Use Case Interactors)  
  * *RICE Score:* 80.0 (Medium Priority / Should Have) | Reach: 80 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* Done  

### **💾 Phase 4: Infrastructure - Persistence & Data Safety**

* **[[TSK-08](TSK-08.md)]: Develop JSONPersistenceAdapter & Atomic Write Protocol**  
  * *Epic Link:* FT-04 (Repository Ports & Safe Adapter)  
  * *RICE Score:* 100.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* Done  
* **[[TSK-12](TSK-12.md)]: Implement Self-Healing Schema Recovery and Disaster Recovery DRP Suite**  
  * *Epic Link:* FT-04 (Repository Ports & Safe Adapter)  
  * *RICE Score:* 90.0 (High Priority / Should Have) | Reach: 90 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  

### **💻 Phase 5: Client Interface (CLI Router, Layout & Logs)**

* **[[TSK-09](TSK-09.md)]: Build CLI Parser and Command Arguments Router**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 100.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* Done  
* **[[TSK-10](TSK-10.md)]: Integrate Telemetry and Unicode CLI Console Badges**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 64.0 (Medium Priority / Should Have) | Reach: 80 / Impact: 1 / Confidence: 0.8 / Effort: 1  
  * *Status:* Done  
* **[[TSK-13](TSK-13.md)]: Implement Handover Report Exporter and Operator Logs**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 80.0 (High Priority / Should Have) | Reach: 80 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  
* **[[TSK-14](TSK-14.md)]: Implement Semi-Visual Terminal Table Renderer and Welcome Interface**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 150.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  
* **[[TSK-15](TSK-15.md)]: Implement Interactive CLI Prompt Shell**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 100.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* Done  
* **[[TSK-16](TSK-16.md)]: Implement Built-in Help Menu & Documentation System**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 100.0 (High Priority / Should Have) | Reach: 100 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  
* **[[TSK-17](TSK-17.md)]: Malicious Input Validation and Shell Hardening**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 90.0 (High Priority / Must Have) | Reach: 90 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  

### **🚀 Phase 6: Packaging & Master Entry Point (Deployable Deliverable)**

* **[[TSK-11](TSK-11.md)]: Establish pyproject.toml Configuration and Unified Main Entry Point**  
  * *Epic Link:* FT-01 & FT-05 (Packaging / Execution)  
  * *RICE Score:* 150.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  

### **📊 Phase 7: Reporting, Search & Notification Extensibility**

* **[[TSK-18](TSK-18.md)]: Exportação de Relatórios em CSV e HTML**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 80.0 (Medium Priority / Should Have) | Reach: 80 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  
* **[[TSK-19](TSK-19.md)]: Busca Avançada de Livros e Leitores**  
  * *Epic Link:* FT-02 & FT-03 (Bounded Domain Objects & Use Case Interactors)  
  * *RICE Score:* 70.0 (Medium Priority / Should Have) | Reach: 70 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  
* **[[TSK-20](TSK-20.md)]: Simulação de Notificação de Atraso por E-mail**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 53.3 (Medium Priority / Could Have) | Reach: 80 / Impact: 2 / Confidence: 1.0 / Effort: 3  
  * *Status:* Done  

### **🔗 Phase 8: Automação de Cobrança & Relatórios Operacionais (Backlog Futuro)**

* **[[TSK-21](TSK-21.md)]: Overdue Book Auto-Suspension Engine**  
  * *Epic Link:* FT-06 (Enforcement & Fine Automation)  
  * *RICE Score:* 90.0 (High Priority / Must Have) | Reach: 90 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  
* **[[TSK-22](TSK-22.md)]: Patron Loan History Report**  
  * *Epic Link:* FT-07 (Audit Reports & Director Dashboard)  
  * *RICE Score:* 80.0 (High Priority / Should Have) | Reach: 80 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  
* **[[TSK-23](TSK-23.md)]: Book Popularity Ranking & Hold Queue Stats**  
  * *Epic Link:* FT-08 (Collection Analytics & Acquisition Planning)  
  * *RICE Score:* 60.0 (Medium Priority / Should Have) | Reach: 60 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* Done  
* **[[TSK-24](TSK-24.md)]: Fine Waiver & Discount Policy Engine**  
  * *Epic Link:* FT-09 (Policy & Rule Engine)  
  * *RICE Score:* 54.0 (Medium Priority / Could Have) | Reach: 90 / Impact: 3 / Confidence: 0.8 / Effort: 4  
  * *Status:* Done  
* **[[TSK-25](TSK-25.md)]: Interactive CLI Shell Startup Usability & Colors**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 64.0 (Medium Priority / Should Have) | Reach: 80 / Impact: 1 / Confidence: 1.0 / Effort: 1  
  * *Status:* Done  
* **[[TSK-26](TSK-26.md)]: Implement Unit of Work (UoW) Pattern**  
  * *Epic Link:* FT-10 (Architectural Resilience)  
  * *RICE Score:* 72.0 (High Priority / Should Have) | Reach: 90 / Impact: 2 / Confidence: 0.8 / Effort: 2  
  * *Status:* To Do  
* **[[TSK-27](TSK-27.md)]: Implement Domain Events & Event Dispatcher**  
  * *Epic Link:* FT-10 (Architectural Resilience)  
  * *RICE Score:* 64.0 (Medium Priority / Should Have) | Reach: 80 / Impact: 2 / Confidence: 0.8 / Effort: 2  
  * *Status:* To Do  
* **[[TSK-28](TSK-28.md)]: Implement Dependency Injection (DI) Container**  
  * *Epic Link:* FT-10 (Architectural Resilience)  
  * *RICE Score:* 48.0 (Medium Priority / Could Have) | Reach: 60 / Impact: 2 / Confidence: 0.8 / Effort: 2  
  * *Status:* To Do  

* **[[TSK-29](TSK-29.md)]: Structured Transaction Journal Logging (Write-Ahead Log)**  
  * *Epic Link:* FT-10 (Architectural Resilience)  
  * *RICE Score:* 81.0 (High Priority / Should Have) | Reach: 90 / Impact: 2 / Confidence: 0.9 / Effort: 2  
  * *Status:* To Do  

* **[[TSK-30](TSK-30.md)]: Refactor God Class CLIController to Adhere to SRP**  
  * *Epic Link:* FT-10 (Architectural Resilience)  
  * *RICE Score:* 144.0 (High Priority / Must Have) | Reach: 90 / Impact: 2 / Confidence: 0.8 / Effort: 1  
  * *Status:* To Do  

* **[[TSK-31](TSK-31.md)]: Testing Coverage Monitoring and CLI Exclusion Policy**  
  * *Epic Link:* FT-10 (Architectural Resilience)  
  * *RICE Score:* 144.0 (High Priority / Must Have) | Reach: 90 / Impact: 2 / Confidence: 0.8 / Effort: 1  
  * *Status:* To Do  

* **[[TSK-32](TSK-32.md)]: i18n Core Translation Service & Registry**  
  * *Epic Link:* FT-10 (Architectural Resilience)  
  * *RICE Score:* 72.0 (High Priority / Should Have) | Reach: 90 / Impact: 2 / Confidence: 0.8 / Effort: 2  
  * *Status:* To Do  

* **[[TSK-33](TSK-33.md)]: UI Presenter CLI Localization Adapter**  
  * *Epic Link:* FT-10 (Architectural Resilience)  
  * *RICE Score:* 72.0 (High Priority / Should Have) | Reach: 90 / Impact: 2 / Confidence: 0.8 / Effort: 2  
  * *Status:* To Do  

* **[[TSK-34](TSK-34.md)]: Interactive Localized Shell UX & Error Badges**  
  * *Epic Link:* FT-10 (Architectural Resilience)  
  * *RICE Score:* 213.75 (High Priority / Should Have) | Reach: 95 / Impact: 2.5 / Confidence: 0.9 / Effort: 1  
  * *Status:* To Do  



---


## **3. 📋 Basic Markdown Kanban Board**

### **🔴 To Do (Ready for Development)**

**Phase 9 — Engenharia Arquitetural Avançada (Melhorias Sênior)**
* [ ] **[[TSK-26](TSK-26.md)]:** Implement Unit of Work (UoW) Pattern
* [ ] **[[TSK-27](TSK-27.md)]:** Implement Domain Events & Event Dispatcher
* [ ] **[[TSK-28](TSK-28.md)]:** Implement Dependency Injection (DI) Container
* [ ] **[[TSK-29](TSK-29.md)]:** Structured Transaction Journal Logging (Write-Ahead Log)
* [ ] **[[TSK-30](TSK-30.md)]:** Refactor God Class CLIController to Adhere to SRP
* [ ] **[[TSK-31](TSK-31.md)]:** Testing Coverage Monitoring and CLI Exclusion Policy
* [ ] **[[TSK-32](TSK-32.md)]:** i18n Core Translation Service & Registry
* [ ] **[[TSK-33](TSK-33.md)]:** UI Presenter CLI Localization Adapter
* [ ] **[[TSK-34](TSK-34.md)]:** Interactive Localized Shell UX & Error Badges




### **🟡 In Progress (Actively Being Built)**

* None

### **🔵 In Review (QA & Test Verification)**

* None

### **🟢 Done (Merged & Verified in Main Trunk)**

* [x] **[[TSK-00](TSK-00.md)]:** Bootstrap project workspace directory layout and initial validation configs
* [x] **[[TSK-01](TSK-01.md)]:** Implement Core Configuration Parser and Logging Setup
* [x] **[[TSK-02](TSK-02.md)]:** Build Domain Entity - BookEntity and FIFO Hold Queue
* [x] **[[TSK-03](TSK-03.md)]:** Build Domain Entities - ReaderEntity & LoanEntity
* [x] **[[TSK-04](TSK-04.md)]:** Develop Domain Services - FineCalculator Engine
* [x] **[[TSK-05](TSK-05.md)]:** Create Application Use Case - CheckoutUseCase
* [x] **[[TSK-06](TSK-06.md)]:** Create Application Use Case - ReturnUseCase
* [x] **[[TSK-07](TSK-07.md)]:** Create Application Use Case - ReserveUseCase
* [x] **[[TSK-08](TSK-08.md)]:** Develop JSONPersistenceAdapter & Atomic Write Protocol
* [x] **[[TSK-12](TSK-12.md)]:** Implement Self-Healing Schema Recovery and Disaster Recovery DRP Suite
* [x] **[[TSK-09](TSK-09.md)]:** Build CLI Parser and Command Arguments Router
* [x] **[[TSK-10](TSK-10.md)]:** Integrate Telemetry and Unicode CLI Console Badges
* [x] **[[TSK-13](TSK-13.md)]:** Implement Handover Report Exporter and Operator Logs
* [x] **[[TSK-14](TSK-14.md)]:** Implement Semi-Visual Terminal Table Renderer and Welcome Interface
* [x] **[[TSK-15](TSK-15.md)]:** Implement Interactive CLI Prompt Shell
* [x] **[[TSK-11](TSK-11.md)]:** Establish pyproject.toml Configuration and Unified Main Entry Point
* [x] **[[TSK-16](TSK-16.md)]:** Implement Built-in Help Menu & Documentation System
* [x] **[[TSK-17](TSK-17.md)]:** Malicious Input Validation and Shell Hardening
* [x] **[[TSK-18](TSK-18.md)]:** Exportação de Relatórios em CSV e HTML
* [x] **[[TSK-19](TSK-19.md)]:** Busca Avançada de Livros e Leitores
* [x] **[[TSK-20](TSK-20.md)]:** Simulação de Notificação de Atraso por E-mail
* [x] **[[TSK-21](TSK-21.md)]:** Overdue Book Auto-Suspension Engine
* [x] **[[TSK-22](TSK-22.md)]:** Patron Loan History Report
* [x] **[[TSK-23](TSK-23.md)]:** Book Popularity Ranking & Hold Queue Stats
* [x] **[[TSK-24](TSK-24.md)]:** Fine Waiver & Discount Policy Engine
* [x] **[[TSK-25](TSK-25.md)]:** Interactive CLI Shell Startup Usability & Colors





