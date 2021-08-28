from app import db
from datetime import datetime
import hashlib

SALT = 'fmksjoifn23j4jmls,fs'


class BaseModelMixin:
    date_creation = db.Column(db.DateTime, default=datetime.now())

    def save(self):
        db.session.add(self)
        db.session.commit()


class User(db.Model, BaseModelMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_superuser = db.Column(db.Boolean, default=False)
    
    def save(self):
        self.password = self.password + SALT
        self.password = hashlib.md5(self.password.encode()).hexdigest()
        super(User, self).save()

    def authenticate(self, password):
        password = password + SALT
        return self.password == hashlib.md5(password.encode()).hexdigest()

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_superuser': self.is_superuser
        }


class Advert(db.Model, BaseModelMixin):
    __tablename__ = 'advert'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True, nullable=False)
    description = db.Column(db.String(), index=True, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'owner': self.owner,
        }

    def update(self, **kwargs):
        self.title = kwargs['title']
        self.description = kwargs['description']
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Token(db.Model, BaseModelMixin):
    __tablename__ = 'token'
    user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    key = db.Column(db.String(), index=True, nullable=True)

    def save(self):
        user = User.query.get(self.user)
        self.key = hashlib.md5(str(user.username + user.email).encode()).hexdigest()
        super(Token, self).save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


db.create_all()
db.session.commit()

# инициализация пользователя
if db.session.query(User).count() == 0:
    password = 'admin' + SALT
    admin = User(username='admin',
                 password=hashlib.md5(password.encode()).hexdigest(),
                 email='admiN@amdin.com',
                 is_superuser=True,
                 is_active=True
                 )
    db.session.add(admin)
    db.session.commit()