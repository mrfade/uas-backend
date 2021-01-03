from flask_restful import Resource, reqparse, request
from flask_restful import fields, marshal_with, marshal, inputs
from models.appointments import Appointment
from models.environments import EnvironmentWorkingHour
from utils.jwt import adminAuthenticated
from utils.dateformat import DateTimeFormat
from app import db
from datetime import datetime

admin_appointment_fields = {
    'id': fields.Integer,
    'start': DateTimeFormat,
    'end': DateTimeFormat,
    'description': fields.String,
    'environment_id': fields.Integer,
    'is_accepted' : fields.Boolean,
}

admin_appointment_list_fields = {
    'count': fields.Integer,
    'appointments': fields.List(fields.Nested(appointment_fields)),
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
admin_appointment_post_parser.add_argument(
    'is_accepted', type=inputs.boolean,location=['json'], help='is_accepted parameter is assigned as default value')

class AdminAppointmentsResource(Resource):
    method_decorators = [adminAuthenticated]

    def get(self, appointment_id=None, admin=None ):
        if appointment_id:
            appointment = Appointment.query.filter_by(id=appointment_id, admin_id=admin.id).first()
            return marshal(appointment, admin_appointment_fields)
        else:
            args = request.args.to_dict()
            limit = args.get('limit', 0)
            offset = args.get('offset', 0)

            args.pop('limit', None)
            args.pop('offset', None)

            appointments = Appointment.query.filter_by(**args, admin_id=admin.id).order_by(Appointment.id)
            if limit:
                appointments = appointments.limit(limit)

            if offset:
                appointments = appointments.offset(offset)

            appointments = appointments.all()            

            return marshal({
                'count': len(appointments),
                'appointments': [marshal(a, admin_appointment_fields) for a in appointments]
            }, admin_appointment_list_fields)

def approveAppointment(self, appointment_id):
    appointment = Appointment.query.filter_by(appointment_id=self.appointment_id).first()
    appointment.is_accepted = True