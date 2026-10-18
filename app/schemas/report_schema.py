from marshmallow import Schema, fields

from app.schemas.common_schema import http_date_field


class ReportSchema(Schema):
    id = fields.Integer()
    user_id = fields.Integer()
    total_value = fields.Decimal(as_string=True, places=2)
    total_expenses = fields.Integer()
    settled_expenses = fields.Integer()
    overdue_expenses = fields.Integer()
    created_at = http_date_field()


class ReportListSchemaResponse(Schema):
    success_message = fields.String()
    reports = fields.List(fields.Nested(ReportSchema))


class ReportDetailSchemaResponse(Schema):
    success_message = fields.String()
    report = fields.Nested(ReportSchema)