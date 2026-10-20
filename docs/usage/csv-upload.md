# Envio de CSV

Em vez de cadastrar despesa por despesa, o usuário pode enviar um arquivo CSV com várias despesas. O processamento acontece em segundo plano, então a resposta do envio apenas confirma o recebimento.

## Como funciona

1. O usuário envia o arquivo em `POST /expenses/csv`.
2. A API valida o arquivo, cria um registro em `attached_csvs` com status `pendente` e publica a task no RabbitMQ.
3. O worker processa o arquivo e grava as despesas.
4. O usuário consulta o status do CSV até ele chegar a `sucesso` ou `erro`.

O detalhamento técnico está em [Processamento de CSV](../architecture/csv-processing.md).

## Acompanhando o resultado

| Rota | Descrição |
|------|-----------|
| `GET /csvs/` | Lista os CSVs enviados pelo usuário, com o status de cada um |
| `GET /csvs/<id>` | Detalha um CSV |
| `DELETE /csvs/<id>` | Remove um CSV |

| Status | O que fazer |
|--------|-------------|
| `pendente` ou `processando` | Aguardar e consultar de novo |
| `sucesso` | As despesas já estão disponíveis em `GET /expenses/` |
| `erro` | Nenhuma despesa foi gravada: corrija o arquivo e envie novamente |

## Formato do arquivo

O CSV precisa ter uma linha de cabeçalho com os nomes das colunas, seguida de uma linha por despesa. Um arquivo sem nenhuma despesa é rejeitado.

| Coluna | Regra |
|--------|-------|
| `title` | Título da despesa (até 50 caracteres) |
| `description` | Descrição da despesa (opcional) |
| `category` | Categoria da despesa (texto de até 50 caracteres) |
| `status` | `pendente`, `pagando`, `quitado` ou `atrasado` |
| `value` | Número válido, com ponto decimal (ex.: `1500.50`) |
| `in_installments` | `true` marca despesa parcelada (maiúsculas ou minúsculas). Qualquer outro valor é tratado como `false` |
| `number_installments` | Inteiro. Obrigatório quando `in_installments` é `true` e deve ficar vazio quando é `false` |
| `register_date` | Obrigatória, no formato `YYYY-MM-DD` |
| `maturity_date` | Obrigatória, no formato `YYYY-MM-DD` |

Exemplo:

```csv
title,description,category,status,value,in_installments,number_installments,register_date,maturity_date
Geladeira,Compra de geladeira nova,Eletrodoméstico,pendente,2500,False,,2026-01-05,2026-01-05
Notebook,Notebook parcelado para trabalho,Eletrônico,pendente,4800,True,6,2026-01-10,2026-02-10
```

!!! info "Quem valida o quê"
    O worker valida `value`, as datas e os campos de parcelas. Os demais campos (`title`, `description`, `category` e `status`) são enviados direto ao banco, que rejeita o que não couber (por exemplo, um `status` fora dos valores permitidos).

## Regras importantes

- **Tudo ou nada**: se uma única linha for inválida (por exemplo, data fora do formato `YYYY-MM-DD` ou `status` fora dos valores permitidos), o CSV inteiro é rejeitado e nada é gravado.
- **O motivo do erro não é exibido**: o sistema registra apenas o status `erro`, sem informar qual linha falhou nem por quê.
- **Sem notificação**: o sistema não avisa quando o processamento termina, por isso é preciso consultar o status.
- **Isolamento**: cada usuário só vê e remove os próprios CSVs.
