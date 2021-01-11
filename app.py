from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions
import settings

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code


for ex in default_exceptions:
    app.register_error_handler(ex, handle_error)

app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config[
    'SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['BUNDLE_ERRORS'] = settings.BUNDLE_ERRORS
app.config['SECRET_KEY'] = settings.SECRET_KEY

db = SQLAlchemy(app)
api = Api(app)
api.prefix = '/api'

from models.admins import Admin
from models.appointments import Appointment
from models.environments import Environment, EnvironmentAdmin, EnvironmentWorkingHour
from models.fixtures import Fixture
from models.users import User, UserStudent, UserStaff

from controllers.admin.auth import AdminAuthLoginResource, AdminAuthRegisterResource
from controllers.admin.environments import AdminEnvironmentsResource, AdminEnvironmentWorkingHoursResource
from controllers.admin.fixtures import AdminFixturesResource
from controllers.admin.appointments import AdminAppointmentsResource, AdminAppointmentApproveResource
from controllers.auth import LoginResource, RegisterResource
from controllers.users import MeResource
from controllers.environments import EnvironmentsResource
from controllers.appointments import AppointmentsResource, AppointmentsAvailableResource

# admin
api.add_resource(AdminAuthLoginResource, '/admin/auth/login')
api.add_resource(AdminAuthRegisterResource, '/admin/auth/register')
api.add_resource(AdminEnvironmentsResource, '/admin/environments',
                 '/admin/environments/<int:environment_id>')
api.add_resource(AdminFixturesResource, '/admin/fixtures',
                 '/admin/fixtures/<int:fixture_id>')
api.add_resource(AdminEnvironmentWorkingHoursResource, '/admin/working_hours')
api.add_resource(AdminAppointmentsResource, '/admin/appointments',
                 '/admin/appointments/<int:appointment_id>')
api.add_resource(AdminAppointmentApproveResource,
                 '/admin/appointments/<int:appointment_id>/approve')

# auth
api.add_resource(LoginResource, '/auth/login')
api.add_resource(RegisterResource, '/auth/register')

# users
api.add_resource(MeResource, '/users/me')

# environments
api.add_resource(EnvironmentsResource, '/environments',
                 '/environments/<int:environment_id>')

# appointments
api.add_resource(AppointmentsResource, '/appointments',
                 '/appointments/<int:appointment_id>')
api.add_resource(AppointmentsAvailableResource,
                 '/appointments/check_available')

if __name__ == '__main__':
    app.run()
