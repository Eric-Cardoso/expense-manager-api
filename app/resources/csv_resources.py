from flask.views import MethodView
from flask_smorest import Blueprint

from app.resources.common import docs_only, protected
from app.schemas.common_schema import ErrorResponseSchema
from app.schemas.csv_schema import CsvDetailSchemaResponse, CsvListSchemaResponse

csv_bp = Blueprint(
    'csv_docs',
    __name__,
    url_prefix='/csvs',
    description='CSVs enviados pelo usuário logado',
)


@csv_bp.route('/')
class Csvs(MethodView):
    @protected(csv_bp)
    @csv_bp.response(200, CsvListSchemaResponse)
    @csv_bp.alt_response(
        404, schema=ErrorResponseSchema, description='Nenhum CSV encontrado'
    )
    @csv_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self):
        docs_only()


@csv_bp.route('/<int:csv_id>')
class CsvById(MethodView):
    @protected(csv_bp)
    @csv_bp.response(200, CsvDetailSchemaResponse)
    @csv_bp.alt_response(
        404, schema=ErrorResponseSchema, description='CSV não encontrado'
    )
    @csv_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self, csv_id):
        docs_only()

    @protected(csv_bp)
    @csv_bp.response(204)
    @csv_bp.alt_response(
        409, schema=ErrorResponseSchema, description='CSV possui despesas vinculadas'
    )
    @csv_bp.alt_response(400, schema=ErrorResponseSchema)
    def delete(self, csv_id):
        docs_only()
