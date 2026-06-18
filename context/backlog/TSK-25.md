# TSK-25: Interactive CLI Shell Startup Usability & Colors

* **Owner / Assignee:** Kalyel N. Laurindo / Software Engineer  
* **Estimated Effort:** 1 Story Point / 4 Hours  
* **Story / Epic Reference:** FT-05 (CLI & Alerts Router)
* **Status:** Done ✅

## 📖 Description & Objectives

Melhorar a usabilidade e a legibilidade da tela de boas-vindas apresentada ao iniciar o console interativo do BiblioModel (`shell`). O comportamento padrão atual exibe apenas um banner básico e uma mensagem genérica de encerramento, forçando novos usuários a adivinhar os comandos disponíveis ou tentar usar barras (como `/help`). Esta tarefa introduz um guia de uso rápido exibido imediatamente na inicialização, escrito inteiramente em inglês, formatado com cores ANSI (verde, amarelo, ciano) destacando comandos recomendados para navegação rápida (`list-books`, `list-readers`, `popularity-report`, `report`, `help`).

## ✅ Definition of Ready (DoR)

* [x] TSK-15 (Interactive CLI Prompt Shell) está completa — a estrutura do loop interativo de shell já está operacional.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **Critério 1 (Mensagem em Inglês & Cores):** Ao iniciar o shell, a tela de boas-vindas deve imprimir instruções rápidas em inglês com cores ANSI destacando comandos.
* [x] **Critério 2 (Dica de Ajuda):** Deve indicar claramente que o usuário pode digitar `help` (sem barras) para ver as regras de negócio completas do acervo.
* [x] **Critério 3 (Lista de Atalhos):** Apresentar atalhos úteis como `list-books`, `list-readers`, `popularity-report` e `report`.
* [x] **Critério 4 (Preservação do Encerramento):** Preservar a instrução de saída `exit` / `quit` de maneira intuitiva.
* [x] **Critério 5 (Testes/Qualidade):** Rodar a suíte inteira de testes e garantir que nenhuma integração existente foi quebrada.
