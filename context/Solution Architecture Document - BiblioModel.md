# **📋 Solution Architecture Document: BiblioModel — Automated Library Loan Tracking & Business Rules Engine**

**Role:** Product Owner / Solution Architect

**Objective:** Define the strategic, commercial, and technical blueprint for resolving the core problem space mapped during discovery.

**Context:** BiblioModel — A lightweight, high-performance, and local-first Python domain rules engine designed to eliminate physical book loss, librarian checkout fatigue, and unrecovered fines in SMB libraries through strict state-machine enforcement and automated loan validation pipelines.

## **🏛️ Project Metadata**

* **Client / Segment:** Municipal and Academic Libraries (SMB Segment)  
* **Date of Creation:** June 12, 2026  
* **Lead Product Owner:** Kalyel Nunes Laurindo / PO  
* **Document Version:** v1.0

## **🚀 1. The Market Opportunity & Strategic Positioning**

In small and mid-sized municipal and academic libraries, operations are heavily bottlenecked by legacy paper-card ledgers and disconnected spreadsheets. These manual workarounds result in a **15% annual inventory shrinkage rate** (lost books) and a **fines recovery rate under 20%**. BiblioModel targets these issues by providing a structured, in-memory domain model with programmatic validation rules. This replaces human-error-prone tracking with an automated, zero-infrastructure CLI engine that enforces borrowing limits, manages reservations, and tracks returns in real time.

### **1.1. Market Size & Opportunity Map (TAM / SAM / SOM)**

Based on public education and municipal library distribution metrics (Inep & SNBP data):

* **Total Addressable Market (TAM):** \~84,000 libraries (covering all public schools, federal/state universities, and municipal public libraries across Brazil).  
* **Serviceable Addressable Market (SAM):** \~15,000 independent municipal libraries, community reading rooms, and regional private/municipal school libraries that lack budget for enterprise cloud systems and need simple, low-overhead, offline-first tools.  
* **Serviceable Obtainable Market (SOM):** 150 local municipal school libraries in Year 1. The goal is to deploy BiblioModel to instantly eliminate their \~$3,600/year in uncollected fines and \~$7,200/year in lost book assets with zero setup costs.

### **1.2. Competitive Landscape & Product Moat**

To position BiblioModel, we analyze existing alternatives against our lightweight, domain-driven value proposition:

* **Competitor A (Enterprise Integrated Library Systems - ILS):** SophiA, Pergamum, KOHA.  
  * *The Gap / Friction Point:* Expensive licensing and support fees, complex database configurations, high hardware requirements, and steep learning curves that overwhelm part-time librarians.  
  * *Our Advantage:* Zero-cost, zero-dependency, instantaneous terminal-based operations, and a clear, clean Python model that can run on any legacy hardware.  
* **Competitor B (Generic Spreadsheets & Office Software):** MS Excel, Google Sheets.  
  * *The Gap / Friction Point:* Excel allows invalid states (e.g., checkout dates in the future), cannot easily handle FIFO reservation queues, lacks automatic status rules, and is prone to corruption when multiple staff edit sheets.  
  * *Our Advantage:* Explicit programmatic domain states (`Available`, `Loaned`, `Overdue`, `Reserved`) with automated constraint validation that blocks invalid transactions.  
* **Manual Workarounds (The "Status Quo"):** Alphabetical paper card boxes.  
  * *The Gap / Friction Point:* High queue times, paper logs get misfiled, calculating overdue days manually takes minutes per transaction, and directors waive fines because records are inconsistent.  
  * *Our Advantage:* Standardized CLI interface, automated fine calculation based on configurable rules, and instant eligibility checkups.

---

## **💰 2. Monetization Strategy, Licensing & Distribution Model**

* **Licensing Model:** Permissive Open-Source MIT License, allowing full modification and adaptation by universities, schools, and local developers.  
* **Primary Pricing / Business Model:** Free & Open Source (FOSS) Portfolio Project. Value lies in demonstrating pristine clean-code and system modeling practices.  
* **Distribution Strategy:** Distributed via GitHub and packaged for PyPI to enable rapid command-line installs (`pip install bibliomodel`) on any computer.  
* **Freemium Loop / Viral Acquisition Tier:** 100% of the domain validation engine and CLI interface are free and open-source, promoting easy adoption by library volunteers and students.

---

## **🛠️ 3. Technical Viability & High-Level Architectural Vision**

To deliver a high-performance system under strict operational constraints, BiblioModel utilizes strategic design choices to address core technical challenges:

* **Challenge 1: Rapid Validation of Patron Eligibility & Book Availability**  
  * *Architectural Solution:* Entirely in-memory domain entities (using Python dictionaries and class-based domain relationships). This guarantees sub-millisecond status checks, ensuring checkouts complete immediately without database roundtrips.  
* **Challenge 2: Preventing Data Loss on Power Failures (Durability)**  
  * *Architectural Solution:* A local-first storage adapter using atomic file writes. Every transaction (loan, return, reservation) triggers a synchronized serialization of the active state to a temporary JSON file, which is then renamed to `db_backup.json` to prevent partial-write corruption.  
* **Challenge 3: FIFO Queue Management for Popular Titles**  
  * *Architectural Solution:* Dedicated domain reservation queues. When a book is reserved, the system appends the reader to a first-in, first-out (FIFO) queue attached to the book instance, blocking other checkouts until the hold is resolved.  
* **Challenge 4: Keeping Rules Configurable Without Modifying Code**  
  * *Architectural Solution:* Externalized configuration parameters. Fine rates per day, maximum allowable concurrent loans, and default loan durations are kept in a standard configuration file (`config.ini`), permitting easy adjustments by library administrators.

### **3.1. Core Architectural Premises**

* **Decoupling Content/Configuration from Code (Content-as-Code):** Daily fine rates, grace periods, and maximum borrow limits are loaded on boot from `config.ini`.  
* **Human-in-the-Loop (HITL) Validation:** Fine waivers cannot happen implicitly. An operator must pass a specific override flag (`--waive --reason "..."`) to clear a balance, creating a recorded trail.  
* **Local-First / Offline-Resilience:** The application runs entirely offline. All inventory and reader records are parsed from the local JSON storage and held in memory.  
* **Privacy-First Data Protection:** Reader names, IDs, and loan histories are saved only on the local machine's disk, preventing data leakage to external networks.

---

## **📑 4. Requirements Engineering & Feature Specification**

### **🎭 4.1. Scenario-Based Requirements Engineering (SBRE)**

* **Scenario A (Book Checkout Eligibility Flow):**  
  * *Trigger:* Librarian runs `bibliomodel loan --reader R101 --book B202`.  
  * *System Action:* The system checks if Reader R101 exists, checks if their current loan count is below the limit (e.g., 3 books), checks if they have any overdue books or outstanding fines, and checks if Book B202 is `Available`. If all checks pass, it updates the book state to `Loaned`, creates a new `Loan` object, persists the state to `db_backup.json`, and outputs a success confirmation.  
* **Scenario B (Book Return & Overdue Fine Assessment):**  
  * *Trigger:* A patron returns a book after the due date. Librarian runs `bibliomodel return --book B202`.  
  * *System Action:* The system locates the active loan, calculates the difference in days between the return date and the due date, applies the daily fine rate from `config.ini`, updates the reader's fine balance, sets the book status to `Available` (or `Reserved` if there is a hold queue), and saves the changes.  
* **Scenario C (FIFO Hold Queue Placement):**  
  * *Trigger:* Reader R102 requests Book B202, which is currently `Loaned`.  
  * *System Action:* The system shifts the book status to `Reserved` and appends Reader R102 to the book's FIFO reservation queue. When B202 is returned, the system automatically marks it as held for Reader R102, preventing others from borrowing it.  
* **Scenario D (Atomic Save Recovery):**  
  * *Trigger:* The host terminal loses power during a return operation.  
  * *System Action:* On the next execution, the system reads `db_backup.json` to restore the in-memory state. If a crash occurred mid-write, the system detects a mismatch, falls back to the `.bak` replica, and log an alert for the operator.

### **🎯 4.2. MoSCoW Prioritization Framework**

#### **🔴 Must Have (Critical for Core Value Proposition & MVP Launch)**

* **RF01: Domain Model State Machine**  
  * *Description:* Implementation of core entities (`Book`, `Reader`, `Loan`) with managed status flows.  
  * *JTBD Tracing:* JTBD #1 - Verify eligibility and availability.  
* **RF02: Loan & Fine Rule Engine**  
  * *Description:* Automatic calculation of late days and fine balances using configurations.  
  * *JTBD Tracing:* JTBD #2 - Compute late fees instantly.  
* **RF03: Dynamic Checkout Constraints**  
  * *Description:* Validation checks that block transactions for suspended readers or reserved books.  
  * *JTBD Tracing:* JTBD #3 - Enforce borrowing limits.  
* **RF04: Local JSON Persistence Adapter**  
  * *Description:* Save and restore memory state to local disk using atomic write operations.  
  * *JTBD Tracing:* JTBD #1 - System durability and offline tracking.

#### **🟡 Should Have (High Value, Target for Immediate Post-MVP Release)**

* **RF05: FIFO Reservation Queues**  
  * *Description:* In-memory queuing system for managing reservation holds on high-demand books.  
  * *JTBD Tracing:* JTBD #1 - Fair queue handling.  
* **RF06: Handover Report Exporter**  
  * *Description:* Generates a `.txt` report containing total active loans, overdue items, and collected fines.  
  * *JTBD Tracing:* JTBD #4 - Auditable records for administration.

#### **🟢 Could Have (Desirable, Nice-to-Have, Low Urgency)**

* **RF07: Basic Operator Logins**  
  * *Description:* Simple command parameter (`--operator "Jane Doe"`) to stamp who authorized overrides.  
  * *JTBD Tracing:* JTBD #5 - Audit tracking.

---

## **⚙️ 5. Non-Functional Requirements (NFRs)**

* **NFR01 (Performance & Latency):** In-memory lookups, state checks, and validations must execute in under 10ms to keep CLI interactions fast.  
* **NFR02 (Portability & OS Compatibility):** Built entirely in Python 3.10+ using only standard library modules (`json`, `datetime`, `configparser`, `argparse`).  
* **NFR03 (Offline Resilience):** Must function 100% offline, with zero dependencies on external databases, APIs, or internet connectivity.  
* **NFR04 (Data Integrity):** Implementation of write-to-tmp-then-rename to ensure no partial writes corrupt the backup database file.  
* **NFR05 (Auditability):** State changes that involve fine waivers or custom overrides must log detailed reasons in a local audit trail.

---

## **📦 6. MVP Scope Boundary (Defining the Line in the Sand)**

### **6.1. Product Focus Area (MVP Scope)**

* **Target Segments:** SMB municipal libraries and academic departments.  
* **Key Flows Included:**  
  1. Interactive CLI checkout flow with borrower eligibility verification.  
  2. Automated fine calculation and balance update on book return.  
  3. Automatic JSON state backup with atomic write protection.

### **6.2. Explicitly OUT of Scope (Post-MVP Backlog)**

* ❌ Automated online payment gateway integrations (payments are processed manually and logged).  
* ❌ Native hardware drivers for physical barcode scanners (scanners behave as standard keyboard inputs).  
* ❌ Web-based GUI or REST API endpoints.  
* ❌ External catalog synchronization protocols (e.g., MARC21).

---

## **🎯 7. Validation Strategy & Success Metrics**

### **7.1. North Star Metric**

**"Average library checkout and return validation time reduced from 3 minutes of manual paper search to under 2 seconds of automated CLI execution."**

### **7.2. Launch Gates & KPIs**

* **Rule Engine Precision:** 100% of loans checked against validation constraints with zero false-positives.  
* **State Machine Integrity:** Zero invalid transitions (e.g., a book cannot transition from `Available` to `Reserved` without a reader queue).  
* **State Recovery Reliability:** 100% recovery of in-memory data from `db_backup.json` after simulated application crashes.

---

## **🎨 8. System Architecture Visualization**

### **8.1. System Context Diagram (Level 1)**

```mermaid
flowchart TD  
    Librarian["🌍 Librarian / Operator<br>(Direct Interaction)"]  

    subgraph Core_System ["🚀 BiblioModel Engine CLI"]  
        Engine["Domain Engine<br>(In-Memory Rules & Validation)"]  
    end

    %% Storage & Configuration  
    Disk["📂 Local Disk Storage<br>(db_backup.json / config.ini)"]  
    Report["📄 daily_handover_report.txt<br>(Local Export)"]  

    %% Connections  
    Librarian -->|Inputs commands & loan actions| Engine  
    Engine -->|Displays validations & fine details| Librarian  
    Engine -->|Loads settings & serializes state| Disk  
    Disk -->|Restores application state on boot| Engine  
    Engine -->|Generates summary reports| Report  

    %% Styling  
    style Engine fill:#f9f,stroke:#333,stroke-width:4px  
    style Core_System fill:#fff,stroke:#333,stroke-dasharray: 5 5  
    style Librarian fill:#def,stroke:#333  
    style Disk fill:#ff9,stroke:#333  
    style Report fill:#bbf,stroke:#333  
```

### **8.2. Container Diagram (Level 2)**

```mermaid
graph TD  
    OperatorCLI((Librarian Terminal))  
      
    subgraph BiblioModel_Engine_Container ["⚙️ BiblioModel Engine Core"]  
        Parser[CLI Argparse Commands Parser]  
        RulesEngine[Domain Rules Validator & State Engine]  
        
        subgraph Memory_State ["🧠 Memory State Dictionary"]  
            ReaderModels[Reader Entities Map]  
            BookModels[Book Entities Map]  
            ActiveLoans[Active Loans Map]  
        end
        
        BackupService[JSON Serialization & Recovery Adapter]  
    end

    subgraph Filesystem_Layer ["📂 Local Disk Filesystem"]  
        BackupJSON[(db_backup.json)]  
        ConfigINI["config.ini"]  
    end

    %% Client Interactions  
    OperatorCLI -->|Command arguments| Parser  
    Parser -->|Routes actions| RulesEngine  
    RulesEngine <-->|Queries & Updates status| Memory_State  
    
    %% Storage Flows  
    ConfigINI -->|Loads thresholds on boot| RulesEngine  
    RulesEngine -->|Triggers save| BackupService  
    BackupService -->|Atomic file write| BackupJSON  
    BackupJSON -->|Loads database on boot| RulesEngine  
      
    %% Styling  
    style BackupJSON fill:#fff,stroke:#f00,stroke-width:2px,stroke-dasharray: 5 5  
    style Memory_State fill:#def,stroke:#333  
    style RulesEngine fill:#f9f,stroke:#333  
```

---

## **⚠️ 9. Engineering Risks & Architecture Assumptions**

* **Engineering Risk 1: System Crash / Power Interruption Mid-Write (State Corruption)**  
  * *Severity:* High  
  * *Mitigation:* Implement atomic file-writing loop. Write serialize output to `db_backup.tmp` first, and then perform an OS-level atomic rename to replace `db_backup.json`.  
* **Engineering Risk 2: Accidental File Modification / Manual Tampering by Users**  
  * *Severity:* Medium  
  * *Mitigation:* Perform schema and constraint validations on boot. If the database file is corrupted or contains illegal JSON structures, prompt the operator to restore from the last automatic backup (`db_backup.json.bak`).  
* **Engineering Risk 3: Insufficient OS Permissions / Directory Lock Failures**  
  * *Severity:* Medium  
  * *Mitigation:* Gracefully handle write permission errors and prompt the user to run the tool from a directory with appropriate access privileges.  
* **Architecture Assumption 1:** The host machine has Python 3.10+ installed and allows local file read/write permissions in the execution folder.  
* **Architecture Assumption 2:** The terminal terminal/CLI is the primary operational interface, and operators will use physical keyboards to type IDs.
