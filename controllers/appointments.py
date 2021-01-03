from flask_restful import Resource, reqparse, request
from flask_restful import fields, marshal_with, marshal, inputs
from models.appointments import Appointment
from models.environments import EnvironmentWorkingHour
from utils.jwt import authenticated
from utils.dateformat import DateTimeFormat
from app import db
from datetime import datetime

appointment_fields = {
    'id': fields.Integer,
    'start': DateTimeFormat,
    'end': DateTimeFormat,
    'description': fields.String,
    'environment_id': fields.Integer,
    'is_accepted' : fields.Boolean,
}

appointment_list_fields = {
    'count': fields.Integer,
    'appointments': fields.List(fields.Nested(appointment_fields)),
}

appointment_post_parser = reqparse.RequestParser()
appointment_post_parser.add_argument(
    'environment_id', type=inputs.positive, required=True, location=['json'], help='environment_id parameter is required')
appointment_post_parser.add_argument(
    'start_date', type=inputs.datetime_from_iso8601, required=True, location=['json'], help='start_date parameter is required')
appointment_post_parser.add_argument(
    'end_date', type=inputs.datetime_from_iso8601, required=True, location=['json'], help='end_date parameter is required')
appointment_post_parser.add_argument(
    'description', type=inputs.regex('^\w{,1000}$'), required=True, location=['json'], help='description parameter is required')
appointment_post_parser.add_argument(
    'is_accepted', type=inputs.boolean,location=['json'], help='is_accepted parameter is assigned as default value')


class AppointmentsResource(Resource):
    method_decorators = [authenticated]

    def get(self, appointment_id=None):
        if appointment_id:
            appointment = Appointment.query.filter_by(id=appointment_id).first()
            return marshal(appointment, appointment_fields)
        else:
            args = request.args.to_dict()
            limit = args.get('limit', 0)
            offset = args.get('offset', 0)

            args.pop('limit', None)
            args.pop('offset', None)

            appointments = Appointment.query.filter_by(**args).order_by(Appointment.id)
            if limit:
                appointments = appointments.limit(limit)

            if offset:
                appointments = appointments.offset(offset)

            appointments = appointments.all()

            return marshal({
                'count': len(appointments),
                'appointments': [marshal(a, appointment_fields) for a in appointments]
            }, appointment_list_fields)

    def post(self, user=None):
        args = appointment_post_parser.parse_args()
        
        user_id = user.id
        start_date = args.start_date
        end_date = args.end_date
        environment_id=args.environment_id
        environmentworkinghour = EnvironmentWorkingHour.query.filter_by(environment_id=environment_id).all()
        appointments = Appointment.query.filter_by(environment_id=environment_id).all()
        
        if(end_date < start_date):
             return {
                    'status': 'error',
                    'message': 'bitiş saati başlangıç saatinden küçük olamaz'
                }, 400

        for working_hours in environmentworkinghour:
            if(start_date < working_hours.start or start_date > working_hours.end or end_date < working_hours.start or end_date > working_hours.end ):
                return {
                    'status': 'error',
                    'message': 'çalışma saatleri içinde değil'
                }, 400
        for a in appointments:
            if ( (a.start <= start_date and start_date < a.end) or (a.start < end_date and end_date <= a.end) or (start_date >= a.start and end_date <= a.end)or(start_date<a.start and end_date>a.end)):
                return {
                    'status': 'error',
                    'message': 'bu saat aralığında randevu alınmıştır'
                }, 400

        appointment = Appointment( start=start_date, end=end_date, description=args.description, environment_id=args.environment_id, user_id=user_id, is_accepted =args.is_accepted)
        db.session.add(appointment)
        db.session.commit()
        
        return marshal({
                'count': len(appointment),
                'appointments': [marshal(a,appointment_fields) for a in appointments]
            }, appointment_list_fields)
