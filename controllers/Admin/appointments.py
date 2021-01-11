from flask_restful import Resource, reqparse, request
from flask_restful import fields, marshal_with, marshal, inputs
from models.appointments import Appointment
from models.environments import EnvironmentWorkingHour, EnvironmentAdmin, Environment
from utils.jwt import adminAuthenticated
from utils.dateformat import DateTimeFormat
from app import db
from datetime import datetime

admin_appointment_fields = {
    'id': fields.Integer,
    'start': DateTimeFormat,
    'end': DateTimeFormat,
    'description': fields.String,
    'user_id': fields.Integer,
    'environment_id': fields.Integer,
    'is_accepted' : fields.Boolean,
}

admin_appointment_list_fields = {
    'count': fields.Integer,
    'appointments': fields.List(fields.Nested(admin_appointment_fields)),
}

admin_appointment_post_parser = reqparse.RequestParser()
admin_appointment_post_parser.add_argument(
    'environment_id', type=inputs.positive, required=True, location=['json'], help='environment_id parameter is required')
admin_appointment_post_parser.add_argument(
    'start_date', type=inputs.datetime_from_iso8601, required=True, location=['json'], help='start_date parameter is required')
admin_appointment_post_parser.add_argument(
    'end_date', type=inputs.datetime_from_iso8601, required=True, location=['json'], help='end_date parameter is required')
admin_appointment_post_parser.add_argument(
    'description', type=inputs.regex('^\w{,1000}$'), required=True, location=['json'], help='description parameter is required')


class AdminAppointmentsResource(Resource):
    method_decorators = [adminAuthenticated]

    def get(self, appointment_id=None, admin=None):
        if appointment_id:
            appointment = Appointment.query.filter_by(id=appointment_id).first_or_404()
            environment_admin = EnvironmentAdmin.query.filter_by(environment_id=appointment.environment_id,admin_id=admin.id).first_or_404()
            return marshal(appointment, admin_appointment_fields)
        else:
            args = request.args.to_dict()
            limit = args.get('limit', 0)
            offset = args.get('offset', 0)

            args.pop('limit', None)
            args.pop('offset', None)

            appointments = EnvironmentAdmin.query.join(Environment, EnvironmentAdmin.environment_id == Environment.id).join(Appointment, Environment.id == Appointment.environment_id).filter_by(**args).order_by(Appointment.id)
            if limit:
                appointments = appointments.limit(limit)

            if offset:
                appointments = appointments.offset(offset)

            appointments = appointments.all()

            return marshal({
                'count': len(appointments),
                'appointments': [marshal(a, admin_appointment_fields) for a in appointments]
            }, admin_appointment_list_fields)


class AdminAppointmentApproveResource(Resource):
    method_decorators = [adminAuthenticated]

    def put(self, appointment_id=None, admin=None):
        appointment = Appointment.query.filter_by(id=appointment_id, admin_id=admin.id).first_or_404()

        appointment.is_accepted = True
        db.session.commit()

        return marshal(appointment, admin_appointment_fields)
