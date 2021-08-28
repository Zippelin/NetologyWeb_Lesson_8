import functools

from sqlalchemy import exc

from models import Token, User
from flask import request, jsonify

ISAUTHENTICATED = 1
ISOWNER = 2


def permission(level, cls=None):
    if level == ISAUTHENTICATED:
        def is_authenticated(f):
            @functools.wraps(f)
            def decorator(*args, **kwargs):
                auth_user = __is_authenticated(request.headers.get('Authentication'))
                kwargs['auth_user'] = auth_user
                if auth_user:
                    return f(*args, **kwargs)
                else:
                    return jsonify({'message': 'you must be authorized'})
            return decorator
        return is_authenticated
    elif level == ISOWNER:
        def is_owner(f):
            @functools.wraps(f)
            def decorator(*args, **kwargs):
                entitie = cls.query.get(kwargs['advert_id'])
                if entitie:
                    if entitie.owner == kwargs['auth_user'].id:
                        return f(*args, **kwargs)
                    else:
                        return jsonify({'message': 'you can modify only your own Advert'})
                else:
                    return jsonify({'message': 'no Advert'})
            return decorator
        return is_owner


def __is_authenticated(token):
    if token:
        token = token.split('Token ')[1]
        try:
            token = Token.query.filter_by(key=token).one()
            return User.query.get(token.user)
        except exc.NoResultFound:
            return False
    return False