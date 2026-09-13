from flask import Blueprint
from app.services.auth_service import login_user

route_auth_bp = Blueprint('auth', __name__, url_prefix='/auth/')

@route_auth_bp.route('/', methods=['POST'])
async def route_login_user() -> dict:
    return await login_user()