# Primeira execução

## Conferindo os serviços

Com o ambiente no ar, confira se os containers estão rodando:

```bash
docker compose ps
```

Você deve ver os serviços da API, do banco, do RabbitMQ e do Celery.

## Acessando a documentação interativa

A API expõe o Swagger gerado pelo `flask-smorest`:

```text
http://localhost:<API_PORT>/docs/swagger
```

`<API_PORT>` é a porta definida no seu `.env`.

## Fluxo básico de uso

1. Crie um usuário em `POST /users/`.
2. Faça login em `POST /auth/login/` e copie o `access_token` da resposta.
3. Envie o token no header das próximas requisições:

    ```text
    Authorization: Bearer <access_token>
    ```

4. Cadastre uma despesa em `POST /expenses/` ou envie um CSV em `POST /expenses/csv`.
5. Consulte as despesas em `GET /expenses/` e o status do processamento do CSV em `GET /csvs/`.

Os detalhes de cada etapa estão na seção [Uso](../usage/authentication.md).

## Recriando o banco do zero

As tabelas são criadas apenas na **primeira** subida do volume do MySQL. Para recomeçar com um banco limpo (isto apaga todos os dados):

```bash
docker compose down -v
docker compose up --build
```
