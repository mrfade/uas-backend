import settings
import jwt
import datetime
from functools import wraps
from flask_restful import abort, request
from models.users import User
from utils.password import check_encrypted_password


def encode_jwt(**kwargs):
    payload = {
        **kwargs,
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=3131)
    }
    return jwt.encode(payload, settings.SECRET_KEY).decode('utf-8')


def authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not getattr(func, 'authenticated', True):
            return func(*args, **kwargs)

        try:
            token_passed = (request.headers['Authorization'].split(' '))[1]
        except KeyError:
            token_passed = None

        if token_passed is not None:
            try:
                data = jwt.decode(token_passed, settings.SECRET_KEY, algorithms=['HS256'])

                user = User.query.filter_by(id=data['user_id']).first()
                if user:
                    return func(user=user, *args, **kwargs)

                abort(401)
            except jwt.exceptions.ExpiredSignatureError:
                return {
                    'status': 'error',
                    'message': 'Token has expired'
                }, 403
            except (
                jwt.exceptions.InvalidTokenError,
                jwt.exceptions.DecodeError,
                jwt.exceptions.InvalidAudienceError,
                jwt.exceptions.InvalidIssuerError,
                jwt.exceptions.InvalidIssuedAtError,
                jwt.exceptions.ImmatureSignatureError,
                jwt.exceptions.InvalidKeyError,
                jwt.exceptions.InvalidAlgorithmError,
                jwt.exceptions.MissingRequiredClaimError
            ):
                return {
                    'status': 'error',
                    'message': 'Invalid Token'
                }, 401
        else:
            return {
                'status': 'error',
                'message': 'Token required'
            }, 401

    return wrapper


def adminAuthenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not getattr(func, 'adminAuthenticated', True):
            return func(*args, **kwargs)

        try:
            token_passed = (request.headers['Authorization'].split(' '))[1]
        except KeyError:
            token_passed = None

        if token_passed is not None:
            try:
                data = jwt.decode(token_passed, settings.SECRET_KEY, algorithms=['HS256'])

                admin = Admin.query.filter_by(id=data['admin_id']).first()
                if admin:
                    return func(admin=admin, *args, **kwargs)

                abort(401)
            except jwt.exceptions.ExpiredSignatureError:
                return {
                    'status': 'error',
                    'message': 'Token has expired'
                }, 403
            except (
                jwt.exceptions.InvalidTokenError,
                jwt.exceptions.DecodeError,
                jwt.exceptions.InvalidAudienceError,
                jwt.exceptions.InvalidIssuerError,
                jwt.exceptions.InvalidIssuedAtError,
                jwt.exceptions.ImmatureSignatureError,
                jwt.exceptions.InvalidKeyError,
                jwt.exceptions.InvalidAlgorithmError,
                jwt.exceptions.MissingRequiredClaimError
            ):
                return {
                    'status': 'error',
                    'message': 'Invalid Token'
                }, 401
        else:
            return {
                'status': 'error',
                'message': 'Token required'
            }, 401

    return wrapper
