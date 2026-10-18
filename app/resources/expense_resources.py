from flask.views import MethodView
from flask_smorest import Blueprint

from app.schemas.common_schema import (
    ErrorResponseSchema,
    MessageResponseSchema
)
from app.schemas.csv_schema import CsvUploadSchemaRequest
from app.schemas.expense_schema import (
    ExpenseDetailSchemaResponse,
    ExpenseListSchemaResponse,
    ExpenseSchemaRequest
)
from app.resources.common import docs_only, protected

expense_bp = Blueprint(
    'expense_docs',
    __name__,
    url_prefix='/expenses',
    description='Despesas do usuário logado'
)


@expense_bp.route('/')
class Expenses(MethodView):
    @protected(expense_bp)
    @expense_bp.arguments(ExpenseSchemaRequest)
    @expense_bp.response(201, MessageResponseSchema)
    @expense_bp.alt_response(400, schema=ErrorResponseSchema)
    def post(self, expense_data):
        docs_only()

    @protected(expense_bp)
    @expense_bp.response(200, ExpenseListSchemaResponse)
    @expense_bp.alt_response(
        404, schema=ErrorResponseSchema, description='Nenhuma despesa'
    )
    @expense_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self):
        docs_only()


@expense_bp.route('/csv')
class ExpensesCsv(MethodView):
    @protected(expense_bp)
    @expense_bp.arguments(CsvUploadSchemaRequest, location='files')
    @expense_bp.response(202, MessageResponseSchema)
    @expense_bp.alt_response(400, schema=ErrorResponseSchema)
    def post(self, files):
        docs_only()


@expense_bp.route('/<int:expense_id>')
class ExpenseById(MethodView):
    @protected(expense_bp)
    @expense_bp.response(200, ExpenseDetailSchemaResponse)
    @expense_bp.alt_response(
        404, schema=ErrorResponseSchema, description='Despesa não encontrada'
    )
    @expense_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self, expense_id):
        docs_only()

    @protected(expense_bp)
    @expense_bp.arguments(ExpenseSchemaRequest)
    @expense_bp.response(200, MessageResponseSchema)
    @expense_bp.alt_response(
        404, schema=ErrorResponseSchema, description='Despesa não encontrada'
    )
    @expense_bp.alt_response(400, schema=ErrorResponseSchema)
    def put(self, expense_data, expense_id):
        docs_only()

    @protected(expense_bp)
    @expense_bp.response(204)
    @expense_bp.alt_response(
        404, schema=ErrorResponseSchema, description='Despesa não encontrada'
    )
    @expense_bp.alt_response(400, schema=ErrorResponseSchema)
    def delete(self, expense_id):
        docs_only()