from flask.views import MethodView
from flask_smorest import Blueprint

from app.resources.common import docs_only
from app.schemas.auth_schema import (
    LoginSchemaRequest,
    LoginSchemaResponse,
    RenewSessionSchemaRequest,
    RenewSessionSchemaResponse,
)
from app.schemas.common_schema import ErrorResponseSchema

auth_bp = Blueprint(
    'auth_docs', __name__, url_prefix='/auth', description='Login e renovação de sessão'
)


@auth_bp.route('/login/')
class Login(MethodView):
    @auth_bp.arguments(LoginSchemaRequest)
    @auth_bp.response(200, LoginSchemaResponse)
    @auth_bp.alt_response(
        401,
        schema=ErrorResponseSchema,
        description='Credenciais inválidas ou erro ao realizar o login',
    )
    def post(self, credentials):
        docs_only()


@auth_bp.route('/renew_session/')
class RenewSession(MethodView):
    @auth_bp.arguments(RenewSessionSchemaRequest)
    @auth_bp.response(200, RenewSessionSchemaResponse)
    @auth_bp.alt_response(
        401,
        schema=ErrorResponseSchema,
        description='Refresh token inválido, expirado ou já revogado',
    )
    def post(self, refresh_data):
        docs_only()
