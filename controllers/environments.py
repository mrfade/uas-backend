from flask_restful import Resource, reqparse, request
from flask_restful import fields, marshal_with, marshal, inputs
from models.environments import Environment
from models.fixtures import Fixture
from utils.jwt import authenticated
from utils.dateformat import DateTimeFormat
from app import db

environment_fields = {
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

environments_list_fields = {
    'count': fields.Integer,
    'environments': fields.List(fields.Nested(environment_fields)),
}

class EnvironmentsResource(Resource):
    method_decorators = [authenticated]

    def get(self, environment_id=None):
        if environment_id:
            environment = Environment.query.filter_by(id=environment_id).first()
            return marshal(environment, environment_fields)
        else:
            args = request.args.to_dict()
            limit = args.get('limit', 0)
            offset = args.get('offset', 0)

            args.pop('limit', None)
            args.pop('offset', None)

            environment = Environment.query.filter_by(**args).order_by(Environment.id)
            if limit:
                environment = environment.limit(limit)

            if offset:
                environment = environment.offset(offset)

            environment = environment.all()

            return marshal({
                'count': len(environment),
                'environments': [marshal(e, environment_fields) for e in environment]
            }, environments_list_fields)

