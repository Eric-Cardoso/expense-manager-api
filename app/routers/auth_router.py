from flask import Blueprint
from app.services.auth_service import login_user, renew_user_session

route_auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@route_auth_bp.route('/login/', methods=['POST'])
async def route_login_user() -> dict:
    return await login_user()


@route_auth_bp.route('/renew_session/', methods=['POST'])
async def route_renew_user_session() -> dict:
    return await renew_user_session()