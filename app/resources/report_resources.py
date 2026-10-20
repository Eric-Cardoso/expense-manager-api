from flask.views import MethodView
from flask_smorest import Blueprint

from app.resources.common import docs_only, protected
from app.schemas.common_schema import ErrorResponseSchema, MessageResponseSchema
from app.schemas.report_schema import (
    ReportDetailSchemaResponse,
    ReportListSchemaResponse,
)

report_bp = Blueprint(
    'report_docs',
    __name__,
    url_prefix='/reports',
    description='Relatórios de despesas do usuário logado',
)


@report_bp.route('/')
class Reports(MethodView):
    @protected(report_bp)
    @report_bp.response(201, MessageResponseSchema)
    @report_bp.alt_response(
        404,
        schema=ErrorResponseSchema,
        description='Nenhuma despesa para gerar o relatório',
    )
    @report_bp.alt_response(400, schema=ErrorResponseSchema)
    def post(self):
        docs_only()

    @protected(report_bp)
    @report_bp.response(200, ReportListSchemaResponse)
    @report_bp.alt_response(
        404, schema=ErrorResponseSchema, description='Nenhum relatório encontrado'
    )
    @report_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self):
        docs_only()


@report_bp.route('/<int:report_id>')
class ReportById(MethodView):
    @protected(report_bp)
    @report_bp.response(200, ReportDetailSchemaResponse)
    @report_bp.alt_response(
        404, schema=ErrorResponseSchema, description='Relatório não encontrado'
    )
    @report_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self, report_id):
        docs_only()

    @protected(report_bp)
    @report_bp.response(204)
    @report_bp.alt_response(400, schema=ErrorResponseSchema)
    def delete(self, report_id):
        docs_only()
