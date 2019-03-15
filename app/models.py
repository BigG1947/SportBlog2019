from app import db, login
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(256), index=True, unique=True)
    description = db.Column(db.Text)
    text = db.Column(db.Text)
    introImg = db.Column(db.String(256))
    idCategory = db.Column(db.Integer, db.ForeignKey('category.id'))
    view = db.Column(db.Integer, default=0, nullable=False)
    dateAdd = db.Column(db.Date, default=datetime.now(), nullable=False)
    comments = db.relationship('Comment', backref='article', lazy='dynamic')


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    src = db.Column(db.String(256), nullable=False)
    dateAdd = db.Column(db.Date, default=datetime.now(), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(256), unique=True, nullable=False)
    articles = db.relationship('Article', backref='categories', lazy='dynamic')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    login = db.Column(db.String(128), nullable=False)
    hashPassword = db.Column(db.String(256), nullable=False)

    def setPassword(self, password):
        self.hashPassword = generate_password_hash(password=password)

    def checkPasswrod(self, password):
        return check_password_hash(self.hashPassword, password)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    id_article = db.Column(db.Integer, db.ForeignKey('article.id'))
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, default=datetime.now())


@login.user_loader
def loadUser(id):
    return User.query.get(id)
