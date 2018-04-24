import os 

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = b'3\x1f\xcc\xf4/\x911\xc4\xe1\xea\xe2\xb9(\xaa\x0cs\x84\x9d&}\xcc\x0c\xb3S'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
