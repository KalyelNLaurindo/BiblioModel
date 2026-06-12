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
  * *Status:* To Do  

### **🧠 Phase 3: Application Use Cases (In-Memory Orchestration)**

* **[[TSK-05](TSK-05.md)]: Create Application Use Case - CheckoutUseCase**  
  * *Epic Link:* FT-03 (Use Case Interactors)  
  * *RICE Score:* 100.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* To Do  
* **[[TSK-06](TSK-06.md)]: Create Application Use Case - ReturnUseCase**  
  * *Epic Link:* FT-03 (Use Case Interactors)  
  * *RICE Score:* 100.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* To Do  
* **[[TSK-07](TSK-07.md)]: Create Application Use Case - ReserveUseCase**  
  * *Epic Link:* FT-03 (Use Case Interactors)  
  * *RICE Score:* 80.0 (Medium Priority / Should Have) | Reach: 80 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* To Do  

### **💾 Phase 4: Infrastructure - Persistence & Data Safety**

* **[[TSK-08](TSK-08.md)]: Develop JSONPersistenceAdapter & Atomic Write Protocol**  
  * *Epic Link:* FT-04 (Repository Ports & Safe Adapter)  
  * *RICE Score:* 100.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* To Do  
* **[[TSK-12](TSK-12.md)]: Implement Self-Healing Schema Recovery and Disaster Recovery DRP Suite**  
  * *Epic Link:* FT-04 (Repository Ports & Safe Adapter)  
  * *RICE Score:* 90.0 (High Priority / Should Have) | Reach: 90 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* To Do  

### **💻 Phase 5: Client Interface (CLI Router, Layout & Logs)**

* **[[TSK-09](TSK-09.md)]: Build CLI Parser and Command Arguments Router**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 100.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* To Do  
* **[[TSK-10](TSK-10.md)]: Integrate Telemetry and Unicode CLI Console Badges**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 64.0 (Medium Priority / Should Have) | Reach: 80 / Impact: 1 / Confidence: 0.8 / Effort: 1  
  * *Status:* To Do  
* **[[TSK-13](TSK-13.md)]: Implement Handover Report Exporter and Operator Logs**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 80.0 (High Priority / Should Have) | Reach: 80 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* To Do  
* **[[TSK-14](TSK-14.md)]: Implement Semi-Visual Terminal Table Renderer and Welcome Interface**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 150.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 2  
  * *Status:* To Do  
* **[[TSK-15](TSK-15.md)]: Implement Interactive CLI Prompt Shell**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 100.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 3  
  * *Status:* To Do  
* **[[TSK-16](TSK-16.md)]: Implement Built-in Help Menu & Documentation System**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 100.0 (High Priority / Should Have) | Reach: 100 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* To Do  
* **[[TSK-17](TSK-17.md)]: Malicious Input Validation and Shell Hardening**  
  * *Epic Link:* FT-05 (CLI & Alerts Router)  
  * *RICE Score:* 90.0 (High Priority / Must Have) | Reach: 90 / Impact: 2 / Confidence: 1.0 / Effort: 2  
  * *Status:* To Do  

### **🚀 Phase 6: Packaging & Master Entry Point (Deployable Deliverable)**

* **[[TSK-11](TSK-11.md)]: Establish pyproject.toml Configuration and Unified Main Entry Point**  
  * *Epic Link:* FT-01 & FT-05 (Packaging / Execution)  
  * *RICE Score:* 150.0 (High Priority / Must Have) | Reach: 100 / Impact: 3 / Confidence: 1.0 / Effort: 2  
  * *Status:* To Do  

---

## **3. 📋 Basic Markdown Kanban Board**

### **🔴 To Do (Ready for Development)**

* [ ] **[[TSK-04](TSK-04.md)]:** Develop Domain Services - FineCalculator Engine
* [ ] **[[TSK-05](TSK-05.md)]:** Create Application Use Case - CheckoutUseCase
* [ ] **[[TSK-06](TSK-06.md)]:** Create Application Use Case - ReturnUseCase
* [ ] **[[TSK-07](TSK-07.md)]:** Create Application Use Case - ReserveUseCase
* [ ] **[[TSK-08](TSK-08.md)]:** Develop JSONPersistenceAdapter & Atomic Write Protocol
* [ ] **[[TSK-12](TSK-12.md)]:** Implement Self-Healing Schema Recovery and Disaster Recovery DRP Suite
* [ ] **[[TSK-09](TSK-09.md)]:** Build CLI Parser and Command Arguments Router
* [ ] **[[TSK-10](TSK-10.md)]:** Integrate Telemetry and Unicode CLI Console Badges
* [ ] **[[TSK-13](TSK-13.md)]:** Implement Handover Report Exporter and Operator Logs
* [ ] **[[TSK-14](TSK-14.md)]:** Implement Semi-Visual Terminal Table Renderer and Welcome Interface
* [ ] **[[TSK-15](TSK-15.md)]:** Implement Interactive CLI Prompt Shell
* [ ] **[[TSK-16](TSK-16.md)]:** Implement Built-in Help Menu & Documentation System
* [ ] **[[TSK-17](TSK-17.md)]:** Malicious Input Validation and Shell Hardening
* [ ] **[[TSK-11](TSK-11.md)]:** Establish pyproject.toml Configuration and Unified Main Entry Point

### **🟡 In Progress (Actively Being Built)**

* None

### **🔵 In Review (QA & Test Verification)**

* None

### **🟢 Done (Merged & Verified in Main Trunk)**

* [x] **[[TSK-00](TSK-00.md)]:** Bootstrap project workspace directory layout and initial validation configs
* [x] **[[TSK-01](TSK-01.md)]:** Implement Core Configuration Parser and Logging Setup
* [x] **[[TSK-02](TSK-02.md)]:** Build Domain Entity - BookEntity and FIFO Hold Queue
* [x] **[[TSK-03](TSK-03.md)]:** Build Domain Entities - ReaderEntity & LoanEntity
