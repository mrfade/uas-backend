from flask_restful import Resource, reqparse, request
from flask_restful import fields, marshal_with, marshal, inputs
from models.environments import Environment
from models.fixtures import Fixture
from utils.jwt import adminAuthenticated
from utils.dateformat import DateTimeFormat
from app import db

admin_fixture_fields = {
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

admin_fixture_list_fields = {
    'count': fields.Integer,
    'environments': fields.List(fields.Nested(admin_fixture_fields)),
}

admin_fixture_post_parser.add_argument(
    'name', type=inputs.regex('^\w{,100}$'), required=True, location=['json'], help='name parameter is required')
admin_fixture_post_parser.add_argument(
    'type', type=inputs.regex('^\w{,50}$'), required=True, location=['json'], help='type parameter is required')
admin_fixture_post_parser.add_argument(
    'size', type=inputs.regex('^\w{,50}$'), required=True, location=['json'], help='size parameter is required')
admin_fixture_post_parser.add_argument(
    'description', type=inputs.regex('\w{,250}^$'), required=True, location=['json'], help='description parameter is required')


class AdminFixturesResource(Resource):
    method_decorators = [adminAuthenticated]

    def get(self, fixture_id=None, admin=None):
        if fixture_id:
            fixture = Fixture.query.filter_by(id=fixture_id, admin_id=admin.id).first()
            return marshal(fixture, admin_fixture_fields)
        else:
            args = request.args.to_dict()
            limit = args.get('limit', 0)
            offset = args.get('offset', 0)

            args.pop('limit', None)
            args.pop('offset', None)

            fixture = Fixture.query.filter_by(**args, admin_id=admin.id).order_by(fixture.id)
            if limit:
                fixture = fixture.limit(limit)

            if offset:
                fixture = fixture.offset(offset)

            fixture = fixture.all()

            return marshal({
                'count': len(fixture),
                'fixtures': [marshal(f, admin_fixture_fields) for f in fixture]
            }, admin_fixture_list_fields)
