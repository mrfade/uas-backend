from flask_restful import Resource, reqparse, request
from flask_restful import fields, marshal_with, marshal, inputs
from models.users import User
from utils.password import encrypt_password
from app import db

user_fields = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
    'tc_number': fields.String,
    'phone': fields.String,
}

user_list_fields = {
    'count': fields.Integer,
    'users': fields.List(fields.Nested(user_fields)),
}

user_post_parser = reqparse.RequestParser()
user_post_parser.add_argument(
    'first_name', type=inputs.regex('^\w{,20}$'), required=True, location=['json'], help='first_name parameter is required')
user_post_parser.add_argument(
    'last_name', type=inputs.regex('^\w{,20}$'), required=True, location=['json'], help='last_name parameter is required')
user_post_parser.add_argument(
    'password', type=inputs.regex('^\w{6,16}$'), required=True, location=['json'], help='password parameter is required')
user_post_parser.add_argument(
    'email', type=inputs.regex('^\w{,100}$'), required=True, location=['json'], help='email parameter is required')
user_post_parser.add_argument(
    'tc_number', type=inputs.regex('^[0-9]{11}$'), required=True, location=['json'], help='tc_number parameter is required')
user_post_parser.add_argument(
    'phone', type=inputs.regex('^[0-9]{10,20}$'), required=True, location=['json'], help='phone parameter is required')


class UsersResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            return marshal(user, user_fields)
        else:
            args = request.args.to_dict()
            limit = args.get('limit', 0)
            offset = args.get('offset', 0)

            args.pop('limit', None)
            args.pop('offset', None)

            user = User.query.filter_by(**args).order_by(User.id)
            if limit:
                user = user.limit(limit)

            if offset:
                user = user.offset(offset)

            user = user.all()

            return marshal({
                'count': len(user),
                'users': [marshal(u, user_fields) for u in user]
            }, user_list_fields)

    @marshal_with(user_fields)
    def post(self):
        args = user_post_parser.parse_args()

        args.password = encrypt_password(args.password)

        user = User(**args)
        db.session.add(user)
        db.session.commit()

        return user

    @marshal_with(user_fields)
    def put(self, user_id=None):
        user = User.query.get(user_id)

        if 'first_name' in request.json:
            user.name = request.json['first_name']
        if 'last_name' in request.json:
            user.name = request.json['last_name']
        if 'email' in request.json:
            user.name = request.json['email']
        if 'tc_number' in request.json:
            user.name = request.json['tc_number']
        if 'phone' in request.json:
            user.name = request.json['phone']

        db.session.commit()
        return user

    @marshal_with(user_fields)
    def delete(self, user_id=None):
        user = User.query.get(user_id)

        db.session.delete(user)
        db.session.commit()

        return user
