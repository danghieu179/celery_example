# Statement for enabling the development environment
DEBUG = True
# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  
# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db/rectangle.sqlite')
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
SQLALCHEMY_DATABASE_TEST_URI = "sqlite:///" + os.path.join(BASE_DIR, 'db/test.sqlite')