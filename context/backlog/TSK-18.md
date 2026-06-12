# TSK-18: Exportação de Relatórios em CSV e HTML

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-05 (CLI & Alerts Router)

## 📖 Description & Objectives

Implementar a capacidade de exportar relatórios estruturados a partir da CLI do BiblioModel. O operador poderá exportar o catálogo de livros, a lista de leitores cadastrados ou o histórico/status de empréstimos em arquivos formato CSV ou HTML (com estilização inline minimalista e limpa). Os arquivos exportados deverão ser salvos em um diretório de saída configurable ou padrão `./reports/`. Todo o código deve utilizar estritamente a biblioteca padrão do Python (`csv` e manipulação manual/templates de string HTML).

## ✅ Definition of Ready (DoR)

* [x] A persistência em memória e as entidades de domínio (`BookEntity`, `ReaderEntity`, `LoanEntity`) devem estar consolidadas.
* [x] O roteador CLI e o interpretador de comandos interativos do Shell estão implementados e funcionais.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Criterion 1 (Functional):** Comando `export --type [books|readers|loans] --format [csv|html] [--output path]` adicionado à CLI e funcional.
* [ ] **Criterion 2 (Quality/Test):** Testes unitários e de integração validam que os arquivos CSV e HTML são criados corretamente e possuem o conteúdo esperado das entidades correspondentes.
* [ ] **Criterion 3 (Security/Resilience):** O diretório de destino do relatório é criado automaticamente caso não exista, e tentativas de salvar fora do diretório do workspace (path traversal) são barradas com alertas.
