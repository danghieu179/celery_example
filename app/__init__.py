# Import flask and template operators
from flask import Flask
# Import SQLAlchemy
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
import config
# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config["CELERY_BROKER_URL"])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


celery = make_celery(app)

# Import a module / component using its blueprint handler variable (rectangle)
from app.rectangle.controllers import rectangle as rectangle

# Register blueprint(s)
app.register_blueprint(rectangle)

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()