# TSK-26: Implement Unit of Work (UoW) Pattern for Atomic Transactional Context

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 3 Story Points / 12 Hours  
* **Story / Epic Reference:** FT-10 (Architectural Resilience)
* **Status:** Done 🟢

## 📖 Description & Objectives

Implementar o padrão de projeto **Unit of Work (Unidade de Trabalho)** utilizando gerenciadores de contexto (`with` em Python) para coordenar a escrita atômica das transações em múltiplos repositórios. Atualmente, os casos de uso chamam salvamentos individuais sequenciais em persistências distintas (ex: `save_book`, `save_reader`, `save_loan`), o que pode acarretar inconsistências caso o sistema seja interrompido no meio da transação. O Unit of Work consolidará as operações em memória e garantirá que a gravação final em disco seja executada como uma única unidade indivisível (Rollback/Commit atômico).

## ✅ Definition of Ready (DoR)

* [x] TSK-08 (JSONPersistenceAdapter) está operacional com gravação em arquivo temporário.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **Critério 1 (Gerenciador de Contexto):** Criar `IUnitOfWork` e seu adaptador gerenciando a abertura e fechamento de contextos seguros (`__enter__` e `__exit__`).
* [x] **Critério 2 (Commit e Rollback):** Caso ocorra qualquer exceção dentro do bloco, nenhuma alteração em memória deve ser consolidada no disco (Rollback). Se fechar com sucesso, o estado é gravado (Commit).
* [x] **Critério 3 (Integração nos Casos de Uso):** Refatorar `CheckoutUseCase` e `ReturnUseCase` para executar operações dentro do contexto do `UnitOfWork`.
* [x] **Critério 4 (Testes Unitários):** Testar rollback sob exceções simuladas garantindo que o banco de dados permaneça inalterado.
