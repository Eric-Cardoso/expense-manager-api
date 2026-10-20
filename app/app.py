from flask import Flask
from flask_smorest import Api

from app.resources.auth_resources import auth_bp
from app.resources.csv_resources import csv_bp
from app.resources.expense_resources import expense_bp
from app.resources.historic_report_resources import historic_report_bp
from app.resources.report_resources import report_bp
from app.resources.user_resources import user_bp
from app.routers.auth_router import route_auth_bp
from app.routers.csv_router import route_csv_bp
from app.routers.expense_router import route_expense_bp
from app.routers.historic_report_router import route_historic_report_bp
from app.routers.report_router import route_report_bp
from app.routers.user_router import route_user_bp

app = Flask(__name__)
app.json.sort_keys = False

app.config['API_TITLE'] = 'Expense Manager API'
app.config['API_VERSION'] = 'v1'
app.config['OPENAPI_VERSION'] = '3.1.0'
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger'
app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'

app.register_blueprint(route_user_bp)
app.register_blueprint(route_auth_bp)
app.register_blueprint(route_expense_bp)
app.register_blueprint(route_csv_bp)
app.register_blueprint(route_report_bp)
app.register_blueprint(route_historic_report_bp)

api = Api(app)

api.spec.components.security_scheme(
    'bearerAuth', {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT'}
)

api.register_blueprint(user_bp)
api.register_blueprint(auth_bp)
api.register_blueprint(expense_bp)
api.register_blueprint(csv_bp)
api.register_blueprint(report_bp)
api.register_blueprint(historic_report_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
