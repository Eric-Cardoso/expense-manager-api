# Banco de dados

O banco é **MySQL** e todo o acesso é feito com **SQL puro**, sem ORM. As tabelas são criadas pelos arquivos `.sql` da pasta `migrations/`, executados automaticamente pelo MySQL na primeira subida do volume.

## Diagrama entidade-relacionamento

```mermaid
erDiagram
    USERS ||--o{ ATTACHED_CSVS : envia
    USERS ||--o{ EXPENSES : possui
    USERS ||--o{ REFRESH_TOKENS : possui
    USERS ||--o{ REPORTS : "tem relatório"
    USERS ||--o{ HISTORIC_REPORTS : "tem histórico mensal"
    ATTACHED_CSVS |o--o{ EXPENSES : origina

    USERS {
        int id PK
        varchar name
        varchar email UK
        varchar password_hash
    }
    ATTACHED_CSVS {
        int id PK
        int user_id FK
        enum status
        datetime attached_at
        boolean valid
    }
    EXPENSES {
        int id PK
        int user_id FK
        int csv_id FK
        varchar title
        text description
        varchar category
        enum status
        decimal value
        boolean in_installments
        int number_installments
        datetime register_date
        datetime maturity_date
    }
    REPORTS {
        int id PK
        int user_id FK
        decimal total_value
        int total_expenses
        int settled_expenses
        int overdue_expenses
        datetime created_at
    }
    HISTORIC_REPORTS {
        int id PK
        int user_id FK
        varchar month_report
        decimal spent_value
        int spent_expenses
        int settled_expenses
        int overdue_expenses
        datetime generated_at
    }
    REFRESH_TOKENS {
        int id PK
        int user_id FK
        varchar token_hash UK
        boolean is_revoked
        datetime expiration_date
        datetime created_at
    }
```

## Tabelas

| Tabela | Descrição |
|--------|-----------|
| `users` | Usuários da API. O `email` é único e a senha é guardada como hash `bcrypt` |
| `attached_csvs` | Cada CSV enviado, com o status do processamento e a flag `valid` |
| `expenses` | Despesas do usuário, cadastradas manualmente ou originadas de um CSV |
| `reports` | Totais consolidados de gastos e dívidas do usuário |
| `historic_reports` | Fechamento mensal dos totais, um registro por usuário e mês |
| `refresh_tokens` | Refresh tokens emitidos, com hash, validade e flag de revogação |

### Valores dos ENUMs

| Coluna | Valores |
|--------|---------|
| `attached_csvs.status` | `pendente`, `processando`, `sucesso`, `erro` |
| `expenses.status` | `pendente`, `pagando`, `quitado`, `atrasado` |

## Decisões de modelagem

- **Chaves estrangeiras com `ON DELETE RESTRICT`**: não é possível apagar um usuário ou CSV que ainda tenha registros dependentes.
- **`csv_id` é opcional**: despesas cadastradas manualmente não têm CSV de origem.
- **`attached_csvs.valid` nasce como `false`**: só vira `true` quando o CSV inteiro é processado com sucesso.
- **Sem tabela de categorias**: as categorias são fixas, definidas como enum no código e validadas no backend.
- **Sem vínculo direto entre `reports` e `expenses`**: os totais são calculados por agregação (`SUM` e `COUNT`) filtrando por `user_id`.
- **`historic_reports` guarda só totais consolidados**: o detalhamento das despesas de um mês é obtido filtrando `expenses` por `user_id` e intervalo de datas. Não é uma foto imutável: reflete os dados atuais daquele período.
- **Despesas parceladas ocupam uma única linha**: veja [Despesas](../usage/expenses.md).
- **Refresh tokens guardados com hash**: o token em texto puro nunca fica no banco.
