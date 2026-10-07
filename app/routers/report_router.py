from flask import Blueprint
from app.auth.decorators import login_required
from app.services.report_service import generate_expenses_report


route_report_bp = Blueprint('report', __name__, url_prefix='/reports')


@route_report_bp.route('/', methods=['POST'])
@login_required
async def route_generate_expenses_report(request_token) -> dict:
    return await generate_expenses_report(request_token=request_token)