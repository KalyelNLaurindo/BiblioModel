# TSK-24: Fine Waiver & Discount Policy Engine

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 4 Story Points / 16 Hours  
* **Story / Epic Reference:** FT-09 (Policy & Rule Engine)

## 📖 Description & Objectives

Implementar um motor de políticas configurável para isenção e desconto de multas, eliminando a inconsistência atual em que cada bibliotecário aplica critérios diferentes de forma discricionária. O `FineCalculator` existente calcula multas brutas, mas não possui nenhum mecanismo de aplicação de regras de desconto ou isenção — isso gera disputas frequentes com leitores e leakage financeiro por waivers informais não registrados. Esta task introduz um sistema de `FinePolicy` (carregado do `config.ini`) com regras predefinidas: isenção para deficientes (100%), desconto por doação de livro (50%), desconto para primeira infração (25%), e isenção por atraso institucional (erro do sistema).

## ✅ Definition of Ready (DoR)

* [x] TSK-04 (FineCalculator Engine) está completa — o cálculo bruto da multa é a entrada do motor de políticas.
* [x] TSK-06 (ReturnUseCase) está completo — o ponto de aplicação da política é durante a devolução.
* [x] TSK-05 (CheckoutUseCase) está completo — o campo `reader_type` está disponível no `ReaderEntity`.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [ ] **Critério 1 (Definição de Políticas):** `FinePolicy` implementada em `src/domain/policy.py` como um conjunto de regras configuráveis carregadas do `config.ini` na seção `[fine_policy]`. Cada regra define: `condition` (ex.: `reader_type=PCD`, `first_offense=true`, `system_delay=true`), `discount_percent`, e `requires_approval` (bool).
* [ ] **Critério 2 (Motor de Aplicação):** `FinePolicyEngine.apply(fine_amount, reader, loan) -> PolicyResult` avalia todas as regras aplicáveis ao contexto e retorna o valor final da multa após descontos, o desconto total aplicado, e as regras que foram ativadas.
* [ ] **Critério 3 (Integração no ReturnUseCase):** `ReturnUseCase` passa o resultado do `FineCalculator` pelo `FinePolicyEngine` antes de finalizar a devolução. O valor final cobrado é o output do motor de políticas — não o valor bruto.
* [ ] **Critério 4 (Auditoria de Waivers):** Toda isenção ou desconto aplicado gera uma entrada `[INFO]` no log de auditoria e um registro no `loan_history.json` com: regra aplicada, valor original, valor final, e o nome do bibliotecário que processou a devolução.
* [ ] **Critério 5 (Regra requires_approval):** Se `requires_approval=true` para a regra ativada, o sistema exibe um prompt de confirmação na CLI antes de aplicar o desconto, exigindo confirmação explícita do operador (`s/n`). Sem confirmação, o desconto não é aplicado.
* [ ] **Critério 6 (Qualidade/Testes):** Testes unitários cobrem: leitor PCD com isenção total (fine=0), leitor comum com primeira infração (25% de desconto), múltiplas regras aplicáveis simultaneamente (descontos são aditivos até 100%), e `requires_approval=true` sem confirmação (desconto não aplicado).
