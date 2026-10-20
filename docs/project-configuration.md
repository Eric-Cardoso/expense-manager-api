# Configuração do projeto

## Variáveis de ambiente

Todas as variáveis ficam no `.env`, criado a partir do `.env.example`.

### Docker / containers

| Variável | Descrição |
|----------|-----------|
| `MYSQL_IMAGE` | Imagem do MySQL usada pelo serviço de banco |
| `RABBITMQ_IMAGE` | Imagem do RabbitMQ usada pelo broker |
| `CONTAINER_DATABASE_NAME` | Nome do container do banco |
| `CONTAINER_API_NAME` | Nome do container da API |
| `CONTAINER_RABBITMQ_NAME` | Nome do container do RabbitMQ |
| `CONTAINER_CELERY_NAME` | Nome do container do Celery |

### Banco de dados e broker

| Variável | Descrição |
|----------|-----------|
| `MYSQL_DATABASE` | Nome do banco criado na primeira subida |
| `MYSQL_USER` / `MYSQL_PASSWORD` | Credenciais do usuário da aplicação |
| `MYSQL_ROOT_PASSWORD` | Senha do usuário `root` do MySQL |
| `DATABASE_HOST` / `DATABASE_PORT` | Endereço e porta do banco usados pela API e pelo worker |
| `RABBITMQ_DEFAULT_USER` / `RABBITMQ_DEFAULT_PASS` | Credenciais do RabbitMQ |
| `RABBITMQ_PORT_INTERFACE` | Porta do painel de administração do RabbitMQ |
| `RABBITMQ_PORT_AMQP` | Porta AMQP, usada pelo Celery para publicar e consumir tasks |

### API

| Variável | Descrição |
|----------|-----------|
| `API_PORT` | Porta em que a API fica disponível no host |

### Tokens

| Variável | Descrição |
|----------|-----------|
| `SECRET_KEY` | Chave usada para assinar os JWTs |
| `ALGORITHM` | Algoritmo de assinatura dos JWTs |
| `ACCESS_TOKEN_EXPIRATION_TIME` | Tempo de vida do access token |
| `REFRESH_TOKEN_EXPIRATION_TIME` | Tempo de vida do refresh token |

!!! info "Valores definidos no projeto"
    Os requisitos do projeto definem **15 minutos** para o access token e **1 semana** para o refresh token.

## Serviços do Docker Compose

| Serviço | Função |
|---------|--------|
| `api` | Aplicação Flask |
| banco | MySQL com as tabelas criadas pelos arquivos de `migrations/` |
| RabbitMQ | Broker das tarefas em segundo plano |
| Celery | Worker que consome as tasks (processamento de CSV e tarefas periódicas) |

O `Dockerfile` é **único e compartilhado**: não define `CMD`, e cada serviço informa o próprio `command` no `docker-compose.yml`.

### Volumes

| Volume | Uso |
|--------|-----|
| `.:/app` (API) | Código-fonte montado no container durante o desenvolvimento |
| `./migrations:/docker-entrypoint-initdb.d` (banco) | O MySQL executa os `.sql` automaticamente na **primeira** subida |
| `mysql_data:/var/lib/mysql` (banco) | Persiste os dados entre reinicializações |

## Celery

| Configuração | Valor |
|--------------|-------|
| Broker | RabbitMQ (sem Redis e sem result backend) |
| `worker_concurrency` | `1` |
| `worker_prefetch_multiplier` | `2` |
| `acks_late` | habilitado |
| Time limits | 300 s e 150 s |

O estado de cada processamento não fica em um result backend: ele é gravado na tabela `attached_csvs`. Veja [Processamento de CSV](architecture/csv-processing.md).

## Task runner (taskipy)

Os comandos do projeto são definidos no `pyproject.toml` e executados com o `taskipy`. A task `run` sobe a aplicação Flask:

```bash
task run
```

## Documentação com MkDocs

O MkDocs roda **fora** do Docker Compose, direto no ambiente virtual:

```bash
pip install mkdocs-material
mkdocs serve
```

Acesse `http://127.0.0.1:8000`. Se a porta estiver ocupada, use `mkdocs serve -a 127.0.0.1:8001`.
