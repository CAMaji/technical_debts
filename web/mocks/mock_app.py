from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from dotenv import load_dotenv
from models.model import db
import os

def init_mock_app() -> Flask: 
    load_dotenv()
    POSTGRES_USER       = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD   = os.getenv('POSTGRES_PASSWORD', 'postgres')
    POSTGRES_DB         = os.getenv('POSTGRES_DB', 'postgres')
    DATABASE_PORT       = os.getenv('DATABASE_PORT', '5432')
    DATABASE_HOST       = os.getenv('DATABASE_HOST', 'postgres')
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "secret!"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{POSTGRES_DB}'
    app.config['SQLALCHEMY_ENABLE_POOL_PRE_PING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app