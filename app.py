from flask import Flask, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions
import settings

app = Flask(__name__)


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

for ex in default_exceptions:
    app.register_error_handler(ex, handle_error)


app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['BUNDLE_ERRORS'] = settings.BUNDLE_ERRORS
app.config['SECRET_KEY'] = settings.SECRET_KEY

db = SQLAlchemy(app)
api = Api(app)
api.prefix = '/api'

from controllers.auth import LoginResource, RegisterResource
from controllers.environments import EnvironmentsResource
from controllers.appointments import AppointmentsResource

api.add_resource(LoginResource, '/auth/login')
api.add_resource(RegisterResource, '/auth/register')
api.add_resource(EnvironmentsResource, '/environments', '/environments/<int:environment_id>')
api.add_resource(AppointmentsResource, '/appointments', '/appointments/<int:appointment_id>')

if __name__ == '__main__':
    app.run()
