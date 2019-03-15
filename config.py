import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'SportBlog.db')
    SQLALCHEMY_TRACK_MODIFICATIONSd = False
    UPLOAD_FOLDER = '/static/uploadImages/'
    SECRET_KEY = 'This-is-secret-key'
