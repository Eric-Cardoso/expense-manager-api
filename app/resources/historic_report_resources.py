from flask.views import MethodView
from flask_smorest import Blueprint

from app.resources.common import docs_only, protected
from app.schemas.common_schema import ErrorResponseSchema
from app.schemas.historic_report_schema import (
    HistoricReportDetailSchemaResponse,
    HistoricReportListSchemaResponse,
)

historic_report_bp = Blueprint(
    'historic_report_docs',
    __name__,
    url_prefix='/historic_reports',
    description='Históricos mensais de relatórios do usuário logado',
)


@historic_report_bp.route('/')
class HistoricReports(MethodView):
    @protected(historic_report_bp)
    @historic_report_bp.response(200, HistoricReportListSchemaResponse)
    @historic_report_bp.alt_response(
        404, schema=ErrorResponseSchema, description='Nenhum histórico encontrado'
    )
    @historic_report_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self):
        docs_only()


@historic_report_bp.route('/<int:historic_report_id>')
class HistoricReportById(MethodView):
    @protected(historic_report_bp)
    @historic_report_bp.response(200, HistoricReportDetailSchemaResponse)
    @historic_report_bp.alt_response(
        404, schema=ErrorResponseSchema, description='Histórico não encontrado'
    )
    @historic_report_bp.alt_response(400, schema=ErrorResponseSchema)
    def get(self, historic_report_id):
        docs_only()

    @protected(historic_report_bp)
    @historic_report_bp.response(204)
    @historic_report_bp.alt_response(400, schema=ErrorResponseSchema)
    def delete(self, historic_report_id):
        docs_only()
