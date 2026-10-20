# Relatórios

O sistema consolida os gastos do usuário em um **relatório atual** e guarda o fechamento de cada mês em um **histórico de relatórios**. Os relatórios são visíveis apenas para o próprio usuário logado.

## Relatório atual

| Campo | Descrição |
|-------|-----------|
| `total_value` | Valor total das despesas |
| `total_expenses` | Quantidade total de despesas |
| `settled_expenses` | Quantidade de despesas quitadas |
| `overdue_expenses` | Quantidade de despesas atrasadas |
| `created_at` | Data de geração |

Os totais são calculados **no próprio SQL**, com agregações (`SUM` e `COUNT`) sobre `expenses` filtrando por `user_id`. O service guarda o resultado em uma variável e só então o repassa para o `INSERT` na tabela `reports`.


## Histórico mensal

| Campo | Descrição |
|-------|-----------|
| `month_report` | Mês a que o fechamento se refere |
| `spent_value` | Valor gasto no mês |
| `spent_expenses` | Quantidade de despesas do mês |
| `settled_expenses` | Quantidade de despesas quitadas |
| `overdue_expenses` | Quantidade de despesas atrasadas |
| `generated_at` | Data em que o fechamento foi gerado |

O fechamento é feito por uma **tarefa periódica do Celery beat** (com `crontab`), que roda no **dia 1 de cada mês** e fecha o mês calendário anterior. A tarefa é registrada em `app/celery.py` por meio do sinal `on_after_configure`.

!!! note "Histórico não é uma foto congelada"
    O histórico guarda apenas os totais. Para ver o detalhe das despesas de um mês, o sistema filtra `expenses` por `user_id` e intervalo de datas, refletindo os dados atuais daquele período.

## Consistência

O service do histórico executa `rollback` em caso de erro, para que um fechamento parcial nunca fique gravado.
