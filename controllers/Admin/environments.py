from flask_restful import Resource, reqparse, request
from flask_restful import fields, marshal_with, marshal, inputs
from models.environments import Environment
from models.fixtures import Fixture
from utils.jwt import adminAuthenticated
from utils.dateformat import DateTimeFormat
from app import db

admin_environment_fields = {
    'id': fields.Integer,
    'location': fields.String,
    'capacity': fields.Integer,
    'type': fields.String,
    'fixtures': fields.List(fields.Nested({
        'id': fields.Integer,
        'name': fields.String,
        'type': fields.String,
        'size': fields.String,
        'description': fields.String
    })),
    'working_hours': fields.List(fields.Nested({
        'id': fields.Integer,
        'start': DateTimeFormat,
        'end': DateTimeFormat
    })),
}

admin_environments_list_fields = {
    'count': fields.Integer,
    'environments': fields.List(fields.Nested(admin_environment_fields)),
}

admin_environment_post_parser = reqparse.RequestParser()
admin_environment_post_parser.add_argument(
    'name', type=inputs.regex('^\w{,100}$'), required=True, location=['json'], help='name parameter is required')
admin_environment_post_parser.add_argument(
    'location', type=inputs.regex('^\w{,100}$'), required=True, location=['json'], help='location parameter is required')
admin_environment_post_parser.add_argument(
    'capacity', type=inputs.positive, required=True, location=['json'], help='capacity parameter is required')
admin_environment_post_parser.add_argument(
    'type', type=inputs.regex('\w{,50}^$'), required=True, location=['json'], help='type parameter is required')


class AdminEnvironmentsResource(Resource):
    method_decorators = [adminAuthenticated]

    def get(self, environment_id=None, admin=None):
        if environment_id:
            environment = Environment.query.filter_by(id=environment_id, admin_id=admin.id).first()
            return marshal(environment, admin_environment_fields)
        else:
            args = request.args.to_dict()
            limit = args.get('limit', 0)
            offset = args.get('offset', 0)

            args.pop('limit', None)
            args.pop('offset', None)

            environment = Environment.query.filter_by(**args, admin_id=admin.id).order_by(Environment.id)
            if limit:
                environment = environment.limit(limit)

            if offset:
                environment = environment.offset(offset)

            environment = environment.all()

            environment = Environment(**args)
            db.session.add(environment)
            db.session.commit()

            return marshal({
                'count': len(environment),
                'environments': [marshal(e, admin_environment_fields) for e in environment]
            }, admin_environments_list_fields)
