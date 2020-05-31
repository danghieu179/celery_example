from app import db


class Rectangle(db.Model):
    rectangle_id = db.Column(db.Integer, primary_key=True)
    a = db.Column(db.Integer, nullable=False)
    b = db.Column(db.Integer, nullable=False)
    area = db.Column(db.Integer)
    perimeter = db.Column(db.Integer)
