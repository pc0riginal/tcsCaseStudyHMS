from flask import Flask
from config import Config
from flask_pymongo import PyMongo
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)
app.config["DEBUG"] = True
app.config.from_object(Config)
mongo = PyMongo(app)
mongo.init_app(app)

from app import routes



