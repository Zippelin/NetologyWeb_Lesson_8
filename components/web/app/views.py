import os

from flask.views import MethodView
from flask import request, jsonify
from sqlalchemy import exc
from sqlalchemy.exc import InvalidRequestError

from app import app
from models import User, Advert, Token
from permissions import permission, ISAUTHENTICATED, ISOWNER
from tasks.task import send_mail, celery_app


class UserView(MethodView):

    @permission(ISAUTHENTICATED)
    def get(self, user_id=None, **kwargs):
        if user_id:
            if kwargs['auth_user'].is_superuser:
                user = User.query.get(user_id)
            else:
                user = kwargs['auth_user']
            return jsonify(user.serialize())
        else:
            if kwargs['auth_user'].is_superuser:
                return jsonify([
                    user.serialize()
                    for user in User.query.all()
                ])
            else:
                return jsonify({'message': 'please specify user'})

    @permission(ISAUTHENTICATED)
    def post(self, **kwargs):
        if kwargs['auth_user'].is_superuser:
            user = User(**request.json)
            try:
                user.save()
                return jsonify(user.serialize())
            except exc.IntegrityError as err:
                return jsonify({'message': 'wrong data'})
        else:
            return jsonify({'message': 'not enough permissions to create user'})


class AdvertView(MethodView):

    def get(self, advert_id=None):
        if advert_id:
            advert = Advert.query.get(advert_id)
            if advert:
                return jsonify(advert.serialize())
            else:
                return jsonify()
        return jsonify([
            adv.serialize()
            for adv in Advert.query.all()
        ])

    @permission(ISAUTHENTICATED)
    def post(self, **kwargs):
        advert = Advert(**request.json)
        advert.owner = kwargs['auth_user'].id
        try:
            advert.save()
            return jsonify(advert.serialize())
        except exc.IntegrityError:
            return jsonify({'message': 'wrong data'})

    @permission(ISAUTHENTICATED)
    @permission(ISOWNER, cls=Advert)
    def patch(self, advert_id, **kwargs):
        advert = Advert.query.get(advert_id)
        advert.update(**request.json)
        return jsonify(advert.serialize())

    def delete(self, advert_id):
        auth_user = is_authenticated(request.headers.get('Authentication'))
        if auth_user:
            advert = Advert.query.get(advert_id)
            if advert.owner == auth_user.id:
                advert.delete()
                return jsonify()
            else:
                return jsonify({'message': 'you can modify only your own Advert'})
        else:
            return jsonify({'message': 'you must be authorized'})


class MailSenderView(MethodView):

    @permission(ISAUTHENTICATED)
    def get(self, task_id=None, **kwargs):
        if task_id:
            try:
                task_id = str(task_id)
            except:
                return jsonify({'message': 'wrong job id'})

            result = celery_app.AsyncResult(task_id)

            if result.ready():
                return jsonify({'message': 'mail send complete'})
            elif result.state == 'PENDING':
                return jsonify({'message': 'wrong job id or task in process'})
            else:
                return jsonify({'message': 'mail send in proccess'})
        return jsonify({'message': 'provide job id'})

    @permission(ISAUTHENTICATED)
    def post(self, **kwargs):
        if request.json and request.json.get('filter'):
            filters = request.json.get('filter')
            try:
                mails = list(*zip(*User.query.filter_by(**filters).with_entities(User.email)))
            except InvalidRequestError:
                return jsonify({'message': 'wrong filter fields'})
        else:
            mails = list(*zip(*User.query.with_entities(User.email).all()))

        job = send_mail.delay(mails)
        return jsonify({'task_id': job.id})


@app.route('/authenticate/', methods=['POST',])
def athenticate():
    try:
        user = User.query.filter_by(username=request.json['username']).one()
    except exc.NoResultFound:
        return jsonify({
            'message': 'no user found'
        })

    if user.authenticate(request.json['password']):

        try:
            token = Token.query.filter_by(user=user.id).one()
        except exc.NoResultFound:
            token = Token(user=user.id)
            token.save()
        return jsonify({'token': 'Token ' + token.key})
    else:
        return jsonify({
            'message': 'wrong credentials'
        })


@app.route('/logout/', methods=['POST',])
def logout():
    token = request.headers.get('Authentication')
    token = token.split('Token ')[1]
    if token:
        try:
            token = Token.query.filter_by(key=token).one()
            token.delete()
            return jsonify()
        except exc.NoResultFound:
            return jsonify({
                'message': 'wrong token provided'
            })
    else:
        return jsonify({
            'message': 'no token provided'
        })


@app.route('/', methods=['GET',])
def home():
    name = os.getenv('name', 'Unknown')
    return f'Hello {name}'


def is_authenticated(token):
    if token:
        token = token.split('Token ')[1]
        try:
            token = Token.query.filter_by(key=token).one()
            return User.query.get(token.user)
        except exc.NoResultFound:
            return False
    return False


app.add_url_rule('/users/<int:user_id>', view_func=UserView.as_view('users_get_unique'), methods=['GET',])
app.add_url_rule('/users', view_func=UserView.as_view('users_get_all'), methods=['GET',])
app.add_url_rule('/users/', view_func=UserView.as_view('users_create'), methods=['POST',])

app.add_url_rule('/advert/<int:advert_id>', view_func=AdvertView.as_view('advert_get_unique'), methods=['GET',])
app.add_url_rule('/advert', view_func=AdvertView.as_view('advert_get_all'), methods=['GET',])
app.add_url_rule('/advert/', view_func=AdvertView.as_view('advert_create'), methods=['POST',])
app.add_url_rule('/advert/<int:advert_id>', view_func=AdvertView.as_view('advert_patch'), methods=['PATCH',])
app.add_url_rule('/advert/<int:advert_id>', view_func=AdvertView.as_view('advert_delete'), methods=['DELETE',])

app.add_url_rule('/mail', view_func=MailSenderView.as_view('mail_post'), methods=['POST',])
app.add_url_rule('/mail/<task_id>', view_func=MailSenderView.as_view('mail_get'), methods=['GET',])
