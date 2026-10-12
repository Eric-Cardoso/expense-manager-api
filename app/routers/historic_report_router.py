from flask import Blueprint
from app.auth.decorators import login_required
from app.services.historic_report_service import (
    get_user_historic_reports, 
    get_user_historic_report,
    delete_user_historic_report
)

route_historic_report_bp = Blueprint(
    'historic_report', __name__, url_prefix='/historics'
)

@route_historic_report_bp.route('/', methods=['GET'])
@login_required
async def route_get_user_historic_reports(request_token) -> list[dict]:
    return await get_user_historic_reports(request_token=request_token)


@route_historic_report_bp.route('/<int:historic_report_id>', methods=['GET'])
@login_required
async def route_get_user_historic_report(
    request_token, 
    historic_report_id
) -> dict:
    
    return await get_user_historic_report(
        request_token=request_token, 
        request_historic_report_id=historic_report_id
    )


@route_historic_report_bp.route('/<int:historic_report_id>', methods=['DELETE'])
@login_required
async def route_delete_user_historic_report(
    request_token, 
    historic_report_id
) -> None:
    
    return await delete_user_historic_report(
        request_token=request_token, 
        request_historic_report_id=historic_report_id
    )