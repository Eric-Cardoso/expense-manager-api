from flask.views import MethodView
from flask_smorest import Blueprint

from app.resources.common import docs_only
from app.schemas.user_schema import (
    RegisterUserSchemaErrorResponse,
    RegisterUserSchemaRequest,
    RegisterUserSchemaResponse,
)

user_bp = Blueprint(
    'user_docs', __name__, url_prefix='/users', description='Cadastro de usuários'
)


@user_bp.route('/')
class Users(MethodView):
    @user_bp.arguments(RegisterUserSchemaRequest)
    @user_bp.response(201, RegisterUserSchemaResponse)
    @user_bp.alt_response(400, schema=RegisterUserSchemaErrorResponse)
    def post(self, user_data):
        docs_only()
