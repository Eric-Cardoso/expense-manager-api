# Instalação

## Requisitos

- Docker e Docker Compose
- Python 3.12+ (apenas para rodar testes, linters e MkDocs fora do container)

## Passo a passo

```bash
# Clone o repositório
git clone https://github.com/Eric-Cardoso/expense-manager-api.git
cd expense-manager-api

# Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate
# Windows: python -m venv venv && venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

## Variáveis de ambiente

```bash
cp .env.example .env
```

Preencha o `.env` com os valores do seu ambiente. Todas as variáveis estão descritas em [Configuração do projeto](../project-configuration.md).

!!! warning "Atenção"
    Nunca versione o `.env`. Use uma `SECRET_KEY` longa e aleatória.

## Subindo o ambiente

```bash
docker compose up --build
```

O comando sobe todos os serviços: API, banco MySQL, RabbitMQ e o worker do Celery. Na primeira execução, o MySQL cria as tabelas automaticamente a partir da pasta `migrations/`.

Siga para a [Primeira execução](first-run.md).
