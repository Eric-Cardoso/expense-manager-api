from marshmallow import Schema, fields

from app.schemas.common_schema import http_date_field


class HistoricReportSchema(Schema):
    id = fields.Integer()
    user_id = fields.Integer()
    month_report = fields.String(metadata={'example': '2026-09-30'})
    spent_value = fields.Decimal(as_string=True, places=2)
    spent_expenses = fields.Integer()
    settled_expenses = fields.Integer()
    overdue_expenses = fields.Integer()
    generated_at = http_date_field()


class HistoricReportListSchemaResponse(Schema):
    success_message = fields.String()
    historic_reports = fields.List(fields.Nested(HistoricReportSchema))


class HistoricReportDetailSchemaResponse(Schema):
    success_message = fields.String()
    historic_report = fields.Nested(HistoricReportSchema)