import sys
from app import db, celery
from flask import Blueprint, request, render_template, jsonify
import sqlalchemy
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker
# Import module models (i.e. User)
from app.rectangle.models import Rectangle
import config
rectangle = Blueprint('rectangle', __name__, url_prefix='/')

def connect(uri_db):
    """Connects to the database and return a session"""
    con = sqlalchemy.create_engine(uri_db)
    # create a Session
    Session = sessionmaker(bind=con)
    session = Session()
    return session

if str(sys.argv[0]) == 'test.py':
    session = connect(config.SQLALCHEMY_DATABASE_TEST_URI)
else:
    session = connect(config.SQLALCHEMY_DATABASE_URI)

def check_value_input(value):
    error = ""
    try:
        value = int(value)
    except ValueError as e:
        value = None
        error = str(e)
    return value, error


@celery.task(name="app.compute_rectangle_by_task")
def compute_rectangle_by_task(rectangle_id, enviroment="production"):
    """[Celery Task]

    Arguments:
        rectangle_id {int} -- Rectangle ID in database

    Keyword Arguments:
        enviroment {str} -- Argument for setup session database(default: {"production"})

    Returns:
        tuple -- Return area and perimeter
    """
    area = perimeter = None
    uri = config.SQLALCHEMY_DATABASE_URI
    if enviroment == "testing":
        uri = config.SQLALCHEMY_DATABASE_TEST_URI
    session = connect(uri)
    rectangle = session.query(Rectangle).get(rectangle_id)
    width = rectangle.a
    height = rectangle.b
    area = width * height
    perimeter = width + height
    rectangle.area = area
    rectangle.perimeter = perimeter
    session.commit()
    return area, perimeter


@rectangle.route("")
def index():
    """ Render homepage """
    return render_template("index.html")


@rectangle.route("createrectangle", methods=["POST"])
def create_rectangle():
    """[summary]
    - Insert new rectangle to database
    Returns:
        Json -- Return Rectangle ID or error
    """
    response_data = {
        "rectangle_id": "",
        "error_rectangle": "",
        "error_width": "",
        "error_height": "",
    }
    json_body = request.get_json()
    width = json_body.get("width", None)
    height = json_body.get("height", None)

    # check value exist in request
    if not width and not height:
        response_data["error_height"] = "This field is requeired"
        response_data["error_width"] = "This field is requeired"
        return jsonify(response_data)

    if not width:
        response_data["error_width"] = "This field is requeired"
        return jsonify(response_data)

    if not height:
        response_data["error_height"] = "This field is requeired"
        return jsonify(response_data)

    # check type of value input
    height, error_height = check_value_input(height)
    if error_height:
        response_data["error_height"] = error_height
    width, error_width = check_value_input(width)
    if error_width:
        response_data["error_width"] = error_width

    if width and height:
        rectangle = Rectangle()
        rectangle.a = width
        rectangle.b = height
        # add new record to db. If process error will rollback
        try:
            db.session.add(rectangle)
            db.session.commit()
            response_data["rectangle_id"] = rectangle.rectangle_id
        except exc.SQLAlchemyError:
            db.session.rollback()
            response_data["error_rectangle"] = "Cannot insert new rectangle to database. Please try again"
            return jsonify(response_data)
    return jsonify(response_data)


@rectangle.route("/computerectangle", methods=["POST", "GET"])
def compute_rectangle():
    """[summary]
    - Call celery task 
    Returns:
        Json -- Return area and permeter of rectangle or error
    """
    response_data = {
        "task_id": "",
        "task_status": "",
        "area": "",
        "perimeter": "",
        "height": "",
        "width": "",
        "error": "",
    }
    json_body = request.get_json()
    if json_body:
        rectangle_id = json_body.get("rectangle_id", None)
        enviroment = json_body.get("enviroment", "production")
    else:
        rectangle_id = request.args.get('rectangle_id', None)
        enviroment = request.args.get('enviroment', "production")
    if not rectangle_id:
        response_data["error"] = "This field is requeired"
        return jsonify(response_data)
    else:
        rectangle_id, error = check_value_input(rectangle_id)
        if error:
            response_data["error"] = error
            return jsonify(response_data)

    rectangle = session.query(Rectangle).get(rectangle_id)
    if not rectangle:
        response_data["error"] = "Rectangle ID hasn't been existed"
        return jsonify(response_data)

    if request.method == 'POST' and not rectangle.area and not rectangle.perimeter:
        # call celery task
        res = compute_rectangle_by_task.s(
            rectangle_id, enviroment).apply_async()
        area, perimeter = compute_rectangle_by_task.AsyncResult(res.id).get()
        if res.status == "SUCCESS":
            area, perimeter = res.get()
            response_data["area"] = area
            response_data["perimeter"] = perimeter
            response_data["width"] = rectangle.a
            response_data["height"] = rectangle.b
        else:
            response_data["error"] = "Can't compute area and perimeter"
    else:
        response_data["width"] = rectangle.a
        response_data["height"] = rectangle.b
        response_data["area"] = rectangle.area
        response_data["perimeter"] = rectangle.perimeter
    return jsonify(response_data)
