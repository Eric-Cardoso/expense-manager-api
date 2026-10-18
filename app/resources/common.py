from typing import NoReturn

from app.schemas.common_schema import ErrorResponseSchema

DOCS_ONLY_MESSAGE = (
    'Blueprint apenas de documentação: a execução real das rotas '
    'fica em app/routers'
)


def docs_only() -> NoReturn:
    raise NotImplementedError(DOCS_ONLY_MESSAGE)


def protected(blp):
    def decorator(func):
        func = blp.alt_response(
            401,
            schema=ErrorResponseSchema,
            description='Token ausente, inválido ou expirado'
        )(func)
        return blp.doc(security=[{'bearerAuth': []}])(func)

    return decorator