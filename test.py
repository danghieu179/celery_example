import os
import unittest
from HtmlTestRunner.runner import HTMLTestRunner
import config
from app import app, db
from app.rectangle.controllers import connect
from app.rectangle.models import Rectangle
session = connect(config.SQLALCHEMY_DATABASE_TEST_URI)


class BasicTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_TEST_URI
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        pass
    """ Test cases from here"""

    def test_001_main_page(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_002_create_rectangle_normal(self):
        response = self.app.post(
            "/createrectangle", json={"width": 10, "height": 12})
        data_json = response.json
        rectangle = session.query(Rectangle).get(data_json["rectangle_id"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(rectangle.a, 10)
        self.assertEqual(rectangle.b, 12)
        self.assertEqual(data_json["rectangle_id"], 1)

    def test_003_create_rectangle_width_abnormal(self):
        response = self.app.post("/createrectangle", json={"height": 12})
        data_json = response.json
        self.assertEqual(data_json["error_width"], "This field is requeired")

    def test_004_create_rectangle_height_abnormal(self):
        response = self.app.post("/createrectangle", json={"width": 12})
        data_json = response.json
        self.assertEqual(data_json["error_height"], "This field is requeired")

    def test_005_create_rectangle_wrong_value_abnormal(self):
        response = self.app.post(
            "/createrectangle", json={"width": "width", "height": "height"})
        data_json = response.json
        self.assertEqual(
            data_json["error_height"], "invalid literal for int() with base 10: 'height'")
        self.assertEqual(
            data_json["error_width"], "invalid literal for int() with base 10: 'width'")

    def test_006_compute_rectangle_normal(self):
        response = self.app.post(
            "/createrectangle", json={"width": 10, "height": 12})
        data_json = response.json
        self.app.post("/computerectangle",
                      json={"rectangle_id": data_json["rectangle_id"], "enviroment": "testing"})
        rectangle = session.query(Rectangle).get(data_json["rectangle_id"])
        self.assertEqual(rectangle.area, 10*12)
        self.assertEqual(rectangle.perimeter, 10+12)

    def test_007_compute_rectangle_non_rectangle_id_abnormal(self):
        self.app.post("/createrectangle", json={"width": 10, "height": 12})
        compute_data = self.app.post(
            "/computerectangle", json={"enviroment": "testing"}).json
        self.assertEqual(compute_data["error"], "This field is requeired")

    def test_008_compute_rectangle_with_rectangle_id_not_existed_abnormal(self):
        self.app.post("/createrectangle", json={"width": 10, "height": 12})
        compute_data = self.app.post(
            "/computerectangle", json={"rectangle_id": 1000, "enviroment": "testing"}).json
        self.assertEqual(compute_data["error"],
                         "Rectangle ID hasn't been existed")

    def test_009_compute_rectangle_with_wrong_value_id_abnormal(self):
        self.app.post("/createrectangle", json={"width": 10, "height": 12})
        compute_data = self.app.post(
            "/computerectangle", json={"rectangle_id": "rectangle_id", "enviroment": "testing"}).json
        self.assertEqual(compute_data["error"],
                         "invalid literal for int() with base 10: 'rectangle_id'")

    def test_010_get_rectangle_with_rectangle_id_normal(self):
        response = self.app.post("/createrectangle", json={"width": 10, "height": 12}).json
        self.app.get(
            "/computerectangle", json={"rectangle_id": response["rectangle_id"], "enviroment": "testing"})
        rectangle = session.query(Rectangle).get(response["rectangle_id"])
        self.assertEqual(rectangle.area, None)
        self.assertEqual(rectangle.perimeter, None)
        self.assertEqual(rectangle.a, 10)
        self.assertEqual(rectangle.b, 12)


if __name__ == "__main__":
    # config report template
    suite = unittest.TestLoader().loadTestsFromTestCase(BasicTests)
    report_output = os.path.dirname(os.path.abspath(__file__)) + "/report"
    report_name = "test_report"
    report_title = "Test Report"
    runner = HTMLTestRunner(output=report_output,
                            report_title=report_title,
                            report_name=report_name,
                            combine_reports=True,
                            add_timestamp=False)
    # run test case
    runner.run(suite)
