from flask_restful import Resource, reqparse, request
from flask_restful import fields, marshal_with, marshal, inputs
from models.admins import Admin
from models.appointments import Appointment
from models.fixtures import Fixture
from utils.jwt import authenticated
from app import db

admin_post_parser = reqparse.RequestParser()
admin_post_parser.add_argument(
    'first_name', type=inputs.regex('^\w{,20}$'), required=True, location=['json'], help='first_name parameter is required')
admin_post_parser.add_argument(
    'last_name', type=inputs.regex('^\w{,20}$'), required=True, location=['json'], help='last_name parameter is required')
admin_post_parser.add_argument(
    'password', type=inputs.regex('^\w{6,16}$'), required=True, location=['json'], help='password parameter is required')
admin_post_parser.add_argument(
    'email', type=inputs.regex('^\w{,100}$'), required=True, location=['json'], help='email parameter is required')
admin_post_parser.add_argument(
    'tc_number', type=inputs.regex('^[0-9]{11}$'), required=True, location=['json'], help='tc_number parameter is required')

class AdminAuthLoginResource(Resource):
    def post(self):
        args = login_post_parser.parse_args()

        email = args.email
        password = args.password

        admin = Admin.query.filter_by(email=email).first()
        try:
            if check_encrypted_password(password, admin.password):
                return {
                    'status': 'success',
                    'access_token': encode_jwt(admin.id)
                }
        except:
            return {
                'status': 'error',
                'message': 'User not found with provided credentials'
            }, 404

class AdminAuthRegisterResource(Resource):
    @marshal_with(register_fields)
    def post(self):
        args = register_post_parser.parse_args()

        email = args.email
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            return {
                'status': 'error',
                'message': 'This email is already in use'
            }, 400

        args.password = encrypt_password(args.password)

        admin = Admin(**args)
        db.session.add(admin)
        db.session.commit()

        return {
            'status': 'success',
            'message': 'Register successfull'
        }















        