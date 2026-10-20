# Endpoints

A documentação interativa completa está no Swagger: `http://localhost:<API_PORT>/docs/swagger`.

## Tabela de rotas
 
### Usuários e autenticação
 
| Método | Rota | Descrição | Auth |
|--------|------|-----------|:----:|
| POST | `/users/` | Cadastra um usuário | — |
| POST | `/auth/login/` | Login (retorna access e refresh token) | — |
| POST | `/auth/renew_session/` | Renova a sessão com o refresh token (retorna um novo par de tokens) | — |
 
### Despesas
 
| Método | Rota | Descrição | Auth |
|--------|------|-----------|:----:|
| POST | `/expenses/` | Cria uma despesa | ✅ |
| GET | `/expenses/` | Lista as despesas do usuário | ✅ |
| GET | `/expenses/<id>` | Detalha uma despesa | ✅ |
| PUT | `/expenses/<id>` | Atualiza uma despesa (payload completo) | ✅ |
| DELETE | `/expenses/<id>` | Remove uma despesa (`204`) | ✅ |
| POST | `/expenses/csv` | Envia um CSV para processamento | ✅ |
 
### CSVs
 
| Método | Rota | Descrição | Auth |
|--------|------|-----------|:----:|
| GET | `/csvs/` | Lista os CSVs enviados e seus status | ✅ |
| GET | `/csvs/<id>` | Detalha um CSV | ✅ |
| DELETE | `/csvs/<id>` | Remove um CSV | ✅ |
 
### Relatórios
 
| Método | Rota | Descrição | Auth |
|--------|------|-----------|:----:|
| POST | `/reports/` | Gera um relatório com os totais atuais do usuário | ✅ |
| GET | `/reports/` | Lista os relatórios do usuário | ✅ |
| GET | `/reports/<id>` | Detalha um relatório | ✅ |
| DELETE | `/reports/<id>` | Remove um relatório | ✅ |
 
### Histórico de relatórios
 
| Método | Rota | Descrição | Auth |
|--------|------|-----------|:----:|
| GET | `/historic_reports/` | Lista os fechamentos mensais do usuário | ✅ |
| GET | `/historic_reports/<id>` | Detalha um fechamento mensal | ✅ |
| DELETE | `/historic_reports/<id>` | Remove um fechamento mensal | ✅ |
 
!!! info "Criação do histórico"
    Não existe rota para criar um item do histórico: ele é gerado pela tarefa periódica que fecha o mês (veja [Relatórios](../usage/reports.md)).

## Convenções de resposta

| Situação | Retorno |
|----------|---------|
| Sucesso em operações simples | Corpo com `success_message` |
| Erro tratado pelo service | Corpo com `error_message` (mensagem genérica em português) |
| Remoção bem-sucedida | `204` sem corpo |
| Token ausente, inválido ou expirado | `401` |
| Falha no cadastro de usuário | `400` |

## Autenticação nas rotas

As rotas marcadas com ✅ exigem o header:

```text
Authorization: Bearer <access_token>
```

Veja os detalhes em [Autenticação](../usage/authentication.md).
