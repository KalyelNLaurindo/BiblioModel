# TSK-45: HTTP REST API Backend Server Integration

* **Owner / Assignee:** Kalyel N. Laurindo / Project Owner  
* **Estimated Effort:** 6 Hours  
* **Story / Epic Reference:** RF12 / HTTP Backend Services  
* **Development Methodology:** TDD & Port-Adapter Pattern

## 📖 Description & Objectives

Expose the BiblioModel business rules engine as an HTTP REST API server. This enables integration with external web apps or mobile frontends by allowing library operations to be performed via HTTP calls.

The server will expose endpoints mapping to the core domain services and use cases:
1. `POST /loans` - Register a book loan (triggers `CheckoutUseCase`).
2. `POST /returns` - Return a book (triggers `ReturnUseCase`).
3. `POST /reservations` - Place a reservation (triggers `ReserveUseCase`).
4. `POST /loans/waive` - Waive fines (triggers `WaiveFineUseCase`).
5. `GET /reports/handover` - Get daily handover report.

## ✅ Definition of Ready (DoR)

* [ ] Endpoint specifications and JSON payload schemas defined.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

### BDD Scenarios (Gherkin Format):

```gherkin
Scenario: Register loan via POST request
  Given the server is running
  When a POST request is sent to "/loans" with payload:
    | reader_id | book_id |
    | R101      | B001    |
  Then the response status code is 201
  And the book is loaned to the reader in the repository

Scenario: Failed checkout due to fine limits returns 400
  Given a reader with unpaid fine balance over the limit
  When a POST request is sent to "/loans" for this reader
  Then the response status code is 400
  And the response contains business rule violation details
```

* [ ] **[Functional]:** REST API server integrated as a new infrastructure adapter in `infra/`.
* [ ] **[Functional]:** Use cases are resolved via DI container and routed correctly from endpoints.
* [ ] **[Verification]:** Test suite covers HTTP request/response flows.
