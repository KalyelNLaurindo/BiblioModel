# TSK-19: Busca Avançada de Livros e Leitores

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 2 Story Points / 8 Hours  
* **Story / Epic Reference:** FT-02 & FT-03 (Bounded Domain Objects & Use Case Interactors)

## 📖 Description & Objectives

Implementar um mecanismo de busca flexível no repositório de dados. O operador deve conseguir pesquisar livros por partes do título ou do autor, e leitores por partes do nome, sem a necessidade de digitar o identificador ID exato. A busca deve ser case-insensitive e tolerar correspondências parciais.

## ✅ Definition of Ready (DoR)

* [x] A persistência em memória e as entidades de domínio (`BookEntity`, `ReaderEntity`) devem estar consolidadas.
* [x] As interfaces de portas de repositórios (`ILibraryRepository`) devem estar definidas para extensão.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **Criterion 1 (Functional):** Comandos `search-books <query>` e `search-readers <query>` integrados ao CLI e ao Shell Interativo.
* [x] **Criterion 2 (Quality/Test):** Testes unitários validam correspondência parcial de strings, filtros vazios e comportamento case-insensitive.
* [x] **Criterion 3 (Architecture):** Lógica de busca deve residir em um Domain Service ou ser exposta por novos métodos de consulta no Repository Port.
