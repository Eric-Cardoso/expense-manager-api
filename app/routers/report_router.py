from flask import Blueprint
from app.auth.decorators import login_required
from app.services.report_service import (
    generate_expenses_report, 
    get_user_reports, 
    get_user_report
)

route_report_bp = Blueprint('report', __name__, url_prefix='/reports')


@route_report_bp.route('/', methods=['POST'])
@login_required
async def route_generate_expenses_report(request_token) -> dict:
    return await generate_expenses_report(request_token=request_token)


@route_report_bp.route('/', methods=['GET'])
@login_required
async def route_get_user_reports(request_token) -> list[dict]:
    return await get_user_reports(request_token=request_token)


@route_report_bp.route('/<int:report_id>', methods=['GET'])
@login_required
async def route_get_user_report(request_token, report_id) -> dict:
    return await get_user_report(
        request_token=request_token,
        request_report_id=report_id
    )