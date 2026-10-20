# Módulos

Mapa completo do que cada parte do código faz. Cada camada segue o mesmo padrão de nomes por funcionalidade: `auth`, `user`, `expense`, `csv`, `report` e `historic_report`.

## `app/`

| Módulo | Responsabilidade |
|--------|------------------|
| `app.py` | Cria o Flask, define a configuração do OpenAPI (`/docs`, Swagger em `/swagger`) e registra os blueprints das rotas |
| `celery.py` | Instância `celery_app` e configuração do worker |

## `app/routers/`

Blueprints com as rotas reais. Cada função recebe a requisição e chama o service correspondente.

| Módulo | Funções |
|--------|---------|
| `user_router.py` | `route_register_user` |
| `auth_router.py` | `route_login_user`, `route_renew_user_session` |
| `expense_router.py` | `route_manually_enter_expense`, `route_get_user_expenses`, `route_register_user_expense_by_csv`, `route_get_user_expense`, `route_manually_update_expense`, `route_delete_user_expense` |
| `csv_router.py` | `route_get_user_csvs`, `route_get_user_csv`, `route_delete_user_csv` |
| `report_router.py` | `route_generate_expenses_report`, `route_get_user_reports`, `route_get_user_report`, `route_delete_user_report` |
| `historic_report_router.py` | `route_get_user_historic_reports`, `route_get_user_historic_report`, `route_delete_user_historic_report` |

## `app/resources/`

Blueprints do `flask-smorest` que apenas **documentam** as rotas no Swagger, sem executar lógica.

| Módulo | Responsabilidade |
|--------|------------------|
| `common.py` | `docs_only` (corpo das rotas de documentação, que nunca executa) e `protected` (marca a rota como protegida no Swagger) |
| `user_resources.py`, `auth_resources.py`, `expense_resources.py`, `csv_resources.py`, `report_resources.py`, `historic_report_resources.py` | Documentação das rotas de cada funcionalidade |

## `app/schemas/`

Schemas usados na documentação das rotas.

| Módulo | Responsabilidade |
|--------|------------------|
| `common_schema.py` | Campos reutilizáveis: `http_date_field` e `flag_field` |
| `user_schema.py`, `auth_schema.py`, `expense_schema.py`, `csv_schema.py`, `report_schema.py`, `historic_report_schema.py` | Schemas de cada funcionalidade |

## `app/services/`

Regras de negócio e validações.

| Módulo | Funções |
|--------|---------|
| `user_service.py` | `register_user` |
| `auth_service.py` | `login_user`, `renew_user_session` |
| `expense_service.py` | `manually_enter_expense`, `get_user_expenses`, `get_user_expense`, `manually_update_expense`, `delete_user_expense`, `register_user_expense_by_csv` |
| `csv_service.py` | `get_user_csvs`, `get_user_csv`, `delete_user_csv` |
| `report_service.py` | `generate_expenses_report`, `get_user_reports`, `get_user_report`, `delete_user_report` |
| `historic_report_service.py` | `generate_user_historic_reports`, `get_user_historic_reports`, `get_user_historic_report`, `delete_user_historic_report` |

!!! note "Funções síncronas"
    `generate_user_historic_reports` é a única função de service síncrona: ela é chamada pela tarefa do Celery que fecha o mês, e não por uma rota.

## `app/repo/`

Acesso ao banco, com queries em SQL puro.

| Módulo | Funções |
|--------|---------|
| `database.py` | `get_connection`, `get_cursor`, `close_connection`, `close_cursor`, `save_data` |
| `user_repo.py` | `insert_user`, `get_user_by_email` |
| `auth_repo.py` | `insert_token_data`, `get_user_token_data`, `update_revoked_token` |
| `expense_repo.py` | `insert_expense`, `insert_expense_by_csv`, `get_expenses`, `get_expense`, `get_calc_expenses`, `update_expense`, `delete_expense` |
| `csv_repo.py` | `insert_csv`, `get_csvs`, `get_csv`, `update_csv`, `delete_csv` |
| `report_repo.py` | `generate_report`, `get_reports`, `get_report`, `delete_report` |
| `historic_report_repo.py` | `get_historic_reports_data`, `generate_historic_reports`, `get_historic_reports`, `get_historic_report`, `delete_historic_report` |

## `app/auth/`

| Módulo | Funções |
|--------|---------|
| `auth_user.py` | `validate_user_email`, `validate_user_password`, `encrypt_password`, `verify_password`, `generate_access_token`, `generate_refresh_token` |
| `decorators.py` | `login_required`: valida o header `Authorization`, decodifica o JWT e responde `401` em qualquer falha |

## `tasks/`

Tasks do Celery, fora do pacote `app`.

| Módulo | Funções |
|--------|---------|
| `csv_tasks.py` | `process_csv`: processa o CSV em segundo plano, com rollback em caso de erro |
| `historic_report_tasks.py` | `setup_periodic_tasks` (agenda as tarefas periódicas) e `close_month` (fecha o histórico mensal) |

## Demais pastas

| Pasta | Conteúdo |
|-------|----------|
| `migrations/` | Arquivos `.sql` que criam as tabelas |
| `tests/` | Testes unitários com pytest, separados por funcionalidade |