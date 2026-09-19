from flask import Flask

from app.routers.auth_router import route_auth_bp
from app.routers.expense_router import route_expense_bp
from app.routers.user_router import route_user_bp


app = Flask(__name__)

app.register_blueprint(route_user_bp)
app.register_blueprint(route_auth_bp)
app.register_blueprint(route_expense_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
   