# TSK-21: Overdue Book Auto-Suspension Engine

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-06 (Enforcement & Fine Automation)

## 📖 Description & Objectives

Implementar um motor de suspensão automática de leitores que excederam o prazo de devolução de um ou mais livros além do threshold configurado. Atualmente, o `BiblioModel` calcula multas via `FineCalculator` mas não altera automaticamente o estado do leitor — a suspensão é aplicada manualmente pelo bibliotecário durante o processo de devolução (`ReturnUseCase`). Isso significa que leitores com semanas de atraso continuam ativos e podem realizar novos empréstimos, gerando perda de acervo. Esta task introduz a verificação automática de elegibilidade de empréstimo com base no tempo de atraso acumulado, blockeando novas retiradas quando o threshold de suspensão é atingido.

## ✅ Definition of Ready (DoR)

* [x] TSK-04 (FineCalculator Engine) está completa — o cálculo de dias de atraso e multa está operacional.
* [x] TSK-05 (CheckoutUseCase) está completo — o fluxo de validação de elegibilidade de empréstimo existe.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Critério 1 (Configuração):** O `config.ini` suporta o campo `[policy] auto_suspend_overdue_days = N` (padrão: 14 dias). Leitores com qualquer livro em atraso superior a N dias têm o status automaticamente alterado para `SUSPENDED`.
* [ ] **Critério 2 (Verificação no Checkout):** `CheckoutUseCase.execute()` consulta todos os empréstimos ativos do leitor antes de processar um novo pedido. Se qualquer livro ultrapassou `auto_suspend_overdue_days`, levanta `ReaderAutoSuspendedError` e bloqueia o novo empréstimo.
* [ ] **Critério 3 (Comando de Varredura):** `bibliomodel check-overdue` executa uma varredura em todos os leitores ativos, aplica suspensão automática conforme a política, e exibe um relatório de quantos leitores foram suspensos nesta execução.
* [ ] **Critério 4 (Reativação Manual):** A suspensão automática só é revertida após a devolução do livro atrasado E o pagamento da multa pendente, via `ReturnUseCase`. A reativação não pode ser feita por comando direto sem esse fluxo.
* [ ] **Critério 5 (Qualidade/Testes):** Testes unitários cobrem: leitor com atraso = N-1 dias (ainda ativo), leitor com atraso = N dias (suspenso), tentativa de checkout de leitor suspenso (levanta `ReaderAutoSuspendedError`), e devolução + pagamento reativa o leitor.
