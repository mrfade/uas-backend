from flask_restful import Resource, reqparse, request
from flask_restful import fields, marshal_with, marshal, inputs
from models.appointments import Appointment
from models.environments import EnvironmentWorkingHour
from utils.jwt import authenticated
from utils.dateformat import DateTimeFormat
from app import db
from datetime import datetime
import pytz

utc = pytz.UTC

appointment_fields = {
    'id': fields.Integer,
    'start': DateTimeFormat,
    'end': DateTimeFormat,
    'description': fields.String,
    'environment_id': fields.Integer,
    'is_accepted': fields.Boolean,
}

appointment_list_fields = {
    'count': fields.Integer,
    'appointments': fields.List(fields.Nested(appointment_fields)),
}

appointment_post_parser = reqparse.RequestParser()
appointment_post_parser.add_argument(
    'environment_id',
    type=inputs.positive,
    required=True,
    location=['json'],
    help='environment_id parameter is required')
appointment_post_parser.add_argument('start_date',
                                     type=inputs.datetime_from_iso8601,
                                     required=True,
                                     location=['json'],
                                     help='start_date parameter is required')
appointment_post_parser.add_argument('end_date',
                                     type=inputs.datetime_from_iso8601,
                                     required=True,
                                     location=['json'],
                                     help='end_date parameter is required')
appointment_post_parser.add_argument('description',
                                     type=inputs.regex('^[\w\W]{,1000}$'),
                                     required=True,
                                     location=['json'],
                                     help='description parameter is required')

appointment_available_post_parser = reqparse.RequestParser()
appointment_available_post_parser.add_argument(
    'environment_id',
    type=inputs.positive,
    required=True,
    location=['json'],
    help='environment_id parameter is required')
appointment_available_post_parser.add_argument(
    'start_date',
    type=inputs.datetime_from_iso8601,
    required=True,
    location=['json'],
    help='start_date parameter is required')
appointment_available_post_parser.add_argument(
    'end_date',
    type=inputs.datetime_from_iso8601,
    required=True,
    location=['json'],
    help='end_date parameter is required')


class AppointmentsResource(Resource):
    method_decorators = [authenticated]

    def get(self, appointment_id=None):
        if appointment_id:
            appointment = Appointment.query.filter_by(
                id=appointment_id).first()
            return marshal(appointment, appointment_fields)
        else:
            args = request.args.to_dict()
            limit = args.get('limit', 0)
            offset = args.get('offset', 0)

            args.pop('limit', None)
            args.pop('offset', None)

            appointments = Appointment.query.filter_by(**args).order_by(
                Appointment.id)
            if limit:
                appointments = appointments.limit(limit)

            if offset:
                appointments = appointments.offset(offset)

            appointments = appointments.all()

            return marshal(
                {
                    'count':
                    len(appointments),
                    'appointments':
                    [marshal(a, appointment_fields) for a in appointments]
                }, appointment_list_fields)

    def post(self, user=None):
        args = appointment_post_parser.parse_args()

        user_id = user.id

        try:
            start_date = args.start_date.replace(tzinfo=utc)
            end_date = args.end_date.replace(tzinfo=utc)
        except ValueError:
            start_date = args.start_date
            end_date = args.end_date

        environment_id = args.environment_id
        environmentworkinghour = EnvironmentWorkingHour.query.filter_by(
            environment_id=environment_id).all()
        appointments = Appointment.query.filter_by(
            environment_id=environment_id).all()

        if (end_date < start_date):
            return {
                'status': 'error',
                'message': 'end time can not be greater than start time'
            }, 400

        in_working_hours = False

        for working_hours in environmentworkinghour:
            wh_start = working_hours.start.replace(tzinfo=utc)
            wh_end = working_hours.end.replace(tzinfo=utc)

            if start_date >= wh_start and start_date < wh_end and end_date > wh_start and end_date <= wh_end:
                in_working_hours = True

        if not in_working_hours:
            return {
                'status': 'error',
                'message': 'time range is not in working hours'
            }, 400

        for a in appointments:
            a_start = a.start.replace(tzinfo=utc)
            a_end = a.end.replace(tzinfo=utc)

            if (a_start <= start_date and start_date < a_end) or (
                    a_start < end_date and end_date <= a_end) or (
                        start_date >= a_start
                        and end_date <= a_end) or (start_date < a_start
                                                   and end_date > a_end):
                return {
                    'status': 'error',
                    'message': 'an appointment is already in the time range'
                }, 400

        appointment = Appointment(start=start_date,
                                  end=end_date,
                                  description=args.description,
                                  environment_id=args.environment_id,
                                  user_id=user_id,
                                  is_accepted=False)
        db.session.add(appointment)
        db.session.commit()

        return marshal(appointment, appointment_fields)


class AppointmentsAvailableResource(Resource):
    def post(self):
        args = appointment_available_post_parser.parse_args()

        start_date = args.start_date.replace(tzinfo=utc)
        end_date = args.end_date.replace(tzinfo=utc)
        environment_id = args.environment_id
        environmentworkinghour = EnvironmentWorkingHour.query.filter_by(
            environment_id=environment_id).all()
        appointments = Appointment.query.filter_by(
            environment_id=environment_id).all()

        if end_date < start_date:
            return {
                'status': 'error',
                'message': 'end time can not be greater than start time'
            }, 400

        in_working_hours = False

        for working_hours in environmentworkinghour:
            wh_start = working_hours.start.replace(tzinfo=utc)
            wh_end = working_hours.end.replace(tzinfo=utc)

            if start_date >= wh_start and start_date < wh_end and end_date > wh_start and end_date <= wh_end:
                in_working_hours = True

        if not in_working_hours:
            return {
                'status': 'error',
                'message': 'time range is not in working hours'
            }, 400

        for a in appointments:
            a_start = a.start.replace(tzinfo=utc)
            a_end = a.end.replace(tzinfo=utc)

            if (a_start <= start_date and start_date < a_end) or (
                    a_start < end_date and end_date <= a_end) or (
                        start_date >= a_start
                        and end_date <= a_end) or (start_date < a_start
                                                   and end_date > a_end):
                return {
                    'status': 'error',
                    'message': 'an appointment is already in the time range'
                }, 400

        return {'status': 'success', 'message': 'available to book'}, 200
