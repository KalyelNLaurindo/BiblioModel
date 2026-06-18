# TSK-22: Patron Loan History Report

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-07 (Audit Reports & Director Dashboard)

## 📖 Description & Objectives

Implementar o relatório de histórico completo de empréstimos por leitor, acessível via CLI com saída em texto formatado (Rich table) e exportação opcional em arquivo de texto estruturado. Atualmente, o `BiblioModel` rastreia empréstimos ativos mas não mantém um histórico acessível de transações encerradas — devoluções concluídas não geram registro persistente além do log de operações. Esta task introduz um repositório de histórico (`LoanHistoryAdapter`) e um comando `bibliomodel reader-history --reader-id <id>` que exibe todos os empréstimos passados e ativos do leitor, com datas, multas pagas e títulos.

## ✅ Definition of Ready (DoR)

* [x] TSK-03 (ReaderEntity & LoanEntity) está completa — os campos de identificação de leitor e empréstimo estão definidos.
* [x] TSK-06 (ReturnUseCase) está completo — o momento de devolução é o trigger para registrar o histórico.
* [x] TSK-08 (JSONPersistenceAdapter) está completo — o mecanismo de escrita atômica pode ser reutilizado para o histórico.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Critério 1 (Persistência de Histórico):** Ao concluir uma devolução via `ReturnUseCase`, o registro do `LoanEntity` (incluindo datas, multa calculada, e status final) é arquivado em `loan_history.json` via `LoanHistoryAdapter`, sem modificar o fluxo atual de persistência do inventário.
* [ ] **Critério 2 (Comando reader-history):** `bibliomodel reader-history --reader-id <id>` exibe uma tabela Rich com: título do livro, data de checkout, data de devolução, dias de atraso, multa aplicada, e status final (RETURNED_ON_TIME / RETURNED_LATE / ACTIVE).
* [ ] **Critério 3 (Filtros):** O comando suporta `--last-n <N>` (últimos N registros) e `--overdue-only` (apenas empréstimos com multa > 0) para facilitar auditorias direcionadas.
* [ ] **Critério 4 (Exportação):** `--export <path>` gera um arquivo `.txt` com o histórico formatado em colunas fixas — adequado para impressão e arquivamento físico pelo diretor.
* [ ] **Critério 5 (Qualidade/Testes):** Testes integrados cobrem: devolução gera registro no histórico, `reader-history` retorna dados corretos para leitor com múltiplos empréstimos, filtro `--overdue-only` exclui empréstimos sem multa, e exportação gera arquivo com o conteúdo esperado.
