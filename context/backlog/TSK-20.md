# TSK-20: Simulação de Notificação de Atraso por E-mail

* **Owner / Assignee:** Developer / AI Agent  
* **Estimated Effort:** 3 Story Points / 12 Hours  
* **Story / Epic Reference:** FT-05 (CLI & Alerts Router)

## 📖 Description & Objectives

Desenvolver uma rotina para varredura diária de empréstimos em atraso e geração de alertas de cobrança. O sistema deve ler os dados de leitores com empréstimos atrasados e gerar uma simulação de envio de e-mail (gravando um log estruturado ou arquivo de texto contendo a mensagem formatada para `./notifications/email_<reader_id>_<date>.txt` ou disparando via `smtplib` em ambiente local/testes se configurado no `config.ini`).

## ✅ Definition of Ready (DoR)

* [x] O serviço de cálculo de multas e controle de datas (`FineCalculator`) e o adapter de configurações (`config.ini`) estão operacionais.
* [x] A persistência de dados em formato JSON recupera corretamente o estado dos empréstimos ativos.

## 🏁 Definition of Done (DoD) & Acceptance Criteria

* [x] **Criterion 1 (Functional):** Comando `notify-overdue` criado na CLI. Gera relatórios textuais de avisos e simula o disparo de mensagens para cada leitor com multas ou atraso pendente.
* [x] **Criterion 2 (Quality/Test):** Testes verificam se o conteúdo da mensagem gerada contém o nome do leitor, títulos atrasados, valor da multa e instruções de devolução.
* [x] **Criterion 3 (Security/Resilience):** O sistema não deve travar se o e-mail do leitor for inválido ou se houver erro simulado de rede/escrita de arquivo.
