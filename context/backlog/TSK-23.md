# TSK-23: Book Popularity Ranking & Hold Queue Stats

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-08 (Collection Analytics & Acquisition Planning)

## 📖 Description & Objectives

Implementar um módulo de análise de popularidade do acervo que rankeia os livros por frequência de empréstimo e tamanho da fila de reserva FIFO. O `BiblioModel` já possui a estrutura de `BookEntity` com fila FIFO de reservas, mas nenhum mecanismo de contabilidade de popularidade — a diretoria da biblioteca não tem dados para decidir quais títulos comprar novas cópias ou quais setores do acervo estão subaproveitados. Esta task introduz um contador de empréstimos por título (`checkout_count`) e o comando `bibliomodel popularity-report` que exibe o ranking completo com fila de espera atual.

## ✅ Definition of Ready (DoR)

* [x] TSK-02 (BookEntity & FIFO Hold Queue) está completa — a estrutura de fila de reserva e identificação de livro estão definidas.
* [x] TSK-05 (CheckoutUseCase) está completo — o fluxo de empréstimo é o ponto de contabilidade.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Critério 1 (Contador de Empréstimos):** `BookEntity` ganha o campo `checkout_count: int = 0` (iniciado em zero, não retroativo). A cada `CheckoutUseCase.execute()` bem-sucedido, `BookEntity.checkout_count` é incrementado em 1 e persistido.
* [ ] **Critério 2 (Ranking de Popularidade):** Comando `bibliomodel popularity-report` exibe uma tabela Rich rankeada por `checkout_count` (decrescente), mostrando: posição no ranking, título, ISBN, total de empréstimos, tamanho atual da fila de reserva, e status de disponibilidade.
* [ ] **Critério 3 (Filtros de Análise):** O comando suporta `--top <N>` (top N mais emprestados), `--with-waitlist` (apenas títulos com fila de espera ativa), e `--underutilized` (livros com 0 empréstimos nos últimos 90 dias — candidatos a descarte ou realocação).
* [ ] **Critério 4 (Recomendação de Aquisição):** Para os top 3 títulos com fila de espera ≥ 3 leitores, o relatório exibe automaticamente uma recomendação de aquisição: `"Recomendação: Adquirir X cópias adicionais de '<Título>'"`.
* [ ] **Critério 5 (Qualidade/Testes):** Testes unitários cobrem: `checkout_count` incrementa corretamente a cada checkout, ranking ordena corretamente com títulos empatados, `--underutilized` filtra apenas livros sem empréstimo no período definido, e recomendação de aquisição é gerada apenas para títulos elegíveis.
