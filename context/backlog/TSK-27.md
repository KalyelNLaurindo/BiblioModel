# TSK-27: Implement Domain Events & Event Dispatcher Architecture

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 3 Story Points / 12 Hours  
* **Story / Epic Reference:** FT-10 (Architectural Resilience)
* **Status:** To Do 🔴

## 📖 Description & Objectives

Desacoplar os Casos de Uso dos seus efeitos colaterais secundários através da introdução de **Eventos de Domínio (Domain Events)**. Atualmente, classes de caso de uso gerenciam diretamente tarefas como gerar logs de auditoria e preparar arquivos de e-mail de notificação. Com essa melhoria, o domínio gerará eventos (como `BookCheckedOut`, `BookReturned`, `FineWaived`), os quais serão publicados em um `EventDispatcher` simples em Python puro. Ouvintes (`Listeners`) dedicados escutarão estes eventos para executar seus respectivos efeitos colaterais de forma isolada.

## ✅ Definition of Ready (DoR)

* [x] TSK-20 (Simulação de Notificação) e TSK-24 (Policy Engine) estão implementadas.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Critério 1 (Event Dispatcher):** Desenvolver um despachador de eventos centralizado no domínio permitindo registrar ouvintes e publicar eventos.
* [ ] **Critério 2 (Eventos Customizados):** Modelar eventos de domínio como objetos de valor imutáveis (`BookLoanedEvent`, `BookReturnedEvent`).
* [ ] **Critério 3 (Desacoplamento):** Refatorar `ReturnUseCase` e `CheckoutUseCase` para disparar eventos ao invés de acionar logs de auditoria e persistência de histórico diretamente.
* [ ] **Critério 4 (Testes Unitários):** Validar que disparar um evento ativa corretamente múltiplos ouvintes registrados.
