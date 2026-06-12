# 📚 Guia Rápido — BiblioModel

**Para quem nunca abriu um terminal antes.** Siga os passos em ordem e em 5 minutos o BiblioModel estará instalado e rodando no seu computador.

---

## Passo 1 — Instale o Python

O BiblioModel funciona com **Python 3.10 ou mais novo**. Se você já tem, pode pular para o Passo 2.

1. Acesse: **https://www.python.org/downloads/**
2. Clique no botão de download amarelo grande (versão estável mais recente)
3. Execute o instalador baixado
4. ⚠️ **IMPORTANTE:** Marque a caixa **"Add Python to PATH"** antes de clicar em *Install Now*

Para confirmar que deu certo, abra o **PowerShell** (Windows) ou **Terminal** (Mac/Linux) e digite:

```bash
python --version
```

Deve retornar algo como `Python 3.10.x` ou superior.

---

## Passo 2 — Baixe o BiblioModel

Você pode clonar usando o Git ou baixar o ZIP direto do GitHub:

### Opção A — Com Git (recomendado)
```bash
git clone https://github.com/KalyelNLaurindo/BiblioModel.git
```

### Opção B — Sem Git
1. Acesse **https://github.com/KalyelNLaurindo/BiblioModel**
2. Clique no botão verde **"Code"** e em **"Download ZIP"**
3. Extraia o arquivo em uma pasta de sua escolha

---

## Passo 3 — Entre na pasta do projeto

No terminal, navegue até a pasta do BiblioModel:

```bash
cd BiblioModel
```

---

## Passo 4 — Instale o programa

Instale o programa localmente no seu computador. O comando abaixo cria o atalho `bibliomodel` automaticamente no terminal:

```bash
pip install .
```

*Nota: Se você for desenvolver ou testar o código, utilize `pip install -e .`.*

---

## ✅ Pronto! Como usar no dia a dia

O BiblioModel funciona através de comandos diretos no terminal. 

### 1. Obter Ajuda e Regras Ativas
Para visualizar todas as regras de negócio carregadas dinamicamente e os comandos disponíveis:
```bash
bibliomodel help
```

---

### 2. Realizar Empréstimo (`loan`)
Empresta um livro (`--book`) para um leitor (`--reader`):
```bash
bibliomodel loan --book B101 --reader R202
```
*   ⚠️ **Importante**: IDs de livros devem começar com **B** e leitores com **R** (ex: `B101`, `R202`). O sistema de hardening de segurança rejeitará qualquer outro formato.

---

### 3. Registrar Devolução (`return`)
Registra a devolução de um livro e calcula multas se houver atraso:
```bash
bibliomodel return --book B101
```

---

### 4. Fazer Reserva (`reserve`)
Se um livro estiver emprestado, coloca um leitor na fila de espera prioritária (FIFO):
```bash
bibliomodel reserve --book B101 --reader R203
```

---

### 5. Perdoar Multa de Leitor (`waive`)
Zera o saldo de multas acumulado por um leitor. Requer o nome do operador e o motivo para fins de auditoria:
```bash
bibliomodel waive --reader R202 --operator "Diretor" --reason "Disputa aceita"
```

---

### 6. Gerar Relatório Diário (`report`)
Gera um arquivo de auditoria chamado `daily_handover_report.txt` e imprime o resumo de métricas na tela em formato de tabela organizada:
```bash
bibliomodel report
```

---

### 7. Consultar Dados Cadastrados
- **Listar Livros**: `bibliomodel list-books`
- **Listar Leitores**: `bibliomodel list-readers`
- **Listar Empréstimos**: `bibliomodel list-loans`

---

### 8. Console Interativo (`shell`)
Se preferir digitar comandos em sequência sem precisar digitar `bibliomodel` toda vez:
```bash
bibliomodel shell
```
Dentro do shell, basta digitar os comandos diretamente (ex: `list-books` ou `loan --book B1 --reader R1`). Digite `exit` para sair.

---

## ❓ Perguntas e Resolução de Problemas

| Situação / Erro | O que fazer |
| :--- | :--- |
| `bibliomodel: comando não encontrado` | Feche seu terminal, abra-o novamente e digite o comando. |
| `Business Rule Error: Reader is suspended` | O leitor possui multas pendentes ou livros em atraso e não pode realizar novos empréstimos até regularizar. |
| `Business Rule Error: Invalid reader ID format` | Certifique-se de que o ID do leitor segue o formato padrão (ex: `R101`) e não possui barras ou pontos (`..`). |
| O banco de dados foi corrompido / apagado | O sistema possui auto-recuperação (Self-Healing). Caso `db_backup.json` seja corrompido, ele carregará o arquivo de backup `.bak` automaticamente para restaurar o estado consistente. |

---

*BiblioModel — Feito com ❤️ por Kalyel Nunes Laurindo | Software Engineer*
