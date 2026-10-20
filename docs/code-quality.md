# Qualidade de código

## Linters

O projeto segue sempre esta ordem:

```bash
isort .
black .
flake8
```

| Ferramenta | Função | Configuração |
|------------|--------|--------------|
| `isort` | Organiza os imports | `profile = "black"` |
| `black` | Formata o código | `skip-string-normalization = true` |
| `flake8` | Aponta o que sobrou | Arquivo `.flake8` |

Por ser o último da cadeia, o `flake8` só reporta o que o `isort` e o `black` não conseguem corrigir sozinhos.

### Configuração do flake8

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = venv, */migrations/*
per-file-ignores = tests/*:E501
```

- `E203` e `W503` são ignorados por conflitarem com o estilo do `black`.
- `per-file-ignores = tests/*:E501` libera o limite de linha **apenas nos testes**, porque nomes de teste descritivos costumam passar de 88 caracteres e o `black` não quebra nome de função. O código de `app/` continua com o limite.

## Testes

```bash
pytest
```

Os testes ficam em `tests/`, separados por funcionalidade (CSV, despesas, relatório e histórico de relatórios), e são **unitários**: não dependem de banco nem de broker.

### Padrões adotados

- **Arrange / Act / Assert**: cada teste segue essa estrutura.
- **Mocks no módulo que usa**: o `patch` aponta para onde a função é importada (por exemplo, `app.services.csv_service`), não para onde ela é definida.
- **Todo mock é conferido**: cada teste verifica seus mocks com `assert_called_once_with` ou `assert_not_called`.
- **Fixtures compartilhadas**: mocks reutilizados (como o do token) ficam em fixtures únicas, em vez de um mock por teste.
- **`datetime` mockado por inteiro**: por ser uma classe imutável, o módulo inteiro é substituído no teste, não apenas o `strptime`.
- **Bibliotecas externas mockadas na origem**: nos testes de autenticação, `bcrypt` e `jwt` são mockados diretamente em `app.auth.auth_user`.

A cobertura é medida com `coverage`, e o arquivo `.coverage` é ignorado pelo Git.

## Convenções de trabalho

- **Issues por funcionalidade**: o trabalho é quebrado em issues no GitHub, com issues de testes separadas por funcionalidade.
- **Commits no padrão Conventional Commits**: mensagens em minúsculo, no formato `feat(escopo): descrição`.

    ```text
    feat(expense): add create expense route
    chore(lint): ignore line length in tests
    ```
