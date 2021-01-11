from flask_restful import Resource, reqparse, request
from flask_restful import fields, marshal
from models.users import User
from utils.jwt import authenticated
from app import db

user_fields = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
    'tc_number': fields.String,
    'phone': fields.String,
}


class MeResource(Resource):
    method_decorators = [authenticated]

    def get(self, user=None):
        user = User.query.filter_by(id=user.id).first_or_404()
        return marshal(user, user_fields)
