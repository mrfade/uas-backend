from flask_restful import Resource, reqparse, request
from flask_restful import fields, marshal_with, marshal, inputs
from models.users import User
from utils.password import encrypt_password, check_encrypted_password
from utils.jwt import encode_jwt
from app import db
import passlib.exc

register_fields = {
    'status': fields.String,
    'message': fields.String,
}

login_post_parser = reqparse.RequestParser()
login_post_parser.add_argument('password',
                               type=inputs.regex('^\w{6,16}$'),
                               required=True,
                               location=['json'],
                               help='password parameter is required')
login_post_parser.add_argument(
    'email',
    type=inputs.regex('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'),
    required=True,
    location=['json'],
    help='email parameter is required')

register_post_parser = reqparse.RequestParser()
register_post_parser.add_argument('first_name',
                                  type=inputs.regex('^\w{,20}$'),
                                  required=True,
                                  location=['json'],
                                  help='first_name parameter is required')
register_post_parser.add_argument('last_name',
                                  type=inputs.regex('^\w{,20}$'),
                                  required=True,
                                  location=['json'],
                                  help='last_name parameter is required')
register_post_parser.add_argument('password',
                                  type=inputs.regex('^\w{6,16}$'),
                                  required=True,
                                  location=['json'],
                                  help='password parameter is required')
register_post_parser.add_argument(
    'email',
    type=inputs.regex('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'),
    required=True,
    location=['json'],
    help='email parameter is required')
register_post_parser.add_argument('tc_number',
                                  type=inputs.regex('^[0-9]{11}$'),
                                  required=True,
                                  location=['json'],
                                  help='tc_number parameter is required')
register_post_parser.add_argument('phone',
                                  type=inputs.regex('^[0-9]{10,20}$'),
                                  required=True,
                                  location=['json'],
                                  help='phone parameter is required')


class LoginResource(Resource):
    def post(self):
        args = login_post_parser.parse_args()

        email = args.email
        password = args.password

        user = User.query.filter_by(email=email).first()
        try:
            if check_encrypted_password(password, user.password):
                return {
                    'status': 'success',
                    'access_token': encode_jwt(user_id=user.id)
                }
        except:
            return {
                'status': 'error',
                'message': 'User not found with provided credentials'
            }, 404


class RegisterResource(Resource):
    @marshal_with(register_fields)
    def post(self):
        args = register_post_parser.parse_args()

        email = args.email
        user = User.query.filter_by(email=email).first()
        if user:
            return {
                'status': 'error',
                'message': 'This email is already in use'
            }, 400

        args.password = encrypt_password(args.password)

        user = User(**args)
        db.session.add(user)
        db.session.commit()

        return {'status': 'success', 'message': 'Register successfull'}
