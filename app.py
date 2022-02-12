from flask import Flask, jsonify, request, json, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from util import object_serializer, convert_for_model
from model import Model
from status import Status

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///prediction.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
CORS(app)


# DB model
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    createdAt = db.Column(db.DateTime)
    outcome = db.Column(db.Text, nullable=False)
    inputs = db.Column(db.Text, nullable=False)

    def __str__(self):
        return f"Prediction(id={self.id}, date-created={self.createdAt}, result={self.outcome}, user-input={self.inputs})"


# initialize db
db.create_all()


# api routes
@app.route('/')
def index():
    return "<h2>Welcome to the flask ML app!</h2>"


@app.route('/api/recent')
def getRecent():
    try:
        obj = Prediction.query.all()
        return jsonify([*map(object_serializer, obj)])
    except:
        return Status(500, "Server error! Could not get data").get()


@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        model = Model()
        request_data = json.loads(request.data)
        converted_data = convert_for_model(request_data)
        return str(model.predict_result(converted_data)[0])
    except:
        return Status(400, "Failed to compute result with given inputs").get()


@app.route('/api/save', methods=["POST"])
def save_predicted():
    try:
        request_data = json.loads(request.data)
        dateObj = datetime.fromisoformat(request_data['createdAt'])
        res = Prediction(createdAt=dateObj,
                         outcome=json.dumps(request_data['outcome']),
                         inputs=json.dumps(request_data['inputs']))
        db.session.add(res)
        db.session.commit()
        return Status(201, "predicted outcome saved successfully").get()
    except:
        return Status(500, "Server error! Could not save data").get()


@app.route('/api/clear/<int:id>', methods=['DELETE'])
def deleteById(id):
    try:
        Prediction.query.filter_by(id=id).delete()
        db.session.commit()
        return Status(200, "recent prediction deleted").get()
    except:
        return Status(500, "Server error! Could not delete data").get()


@app.route('/api/clear/all', methods=['DELETE'])
def deleteAll():
    try:
        Prediction.query.delete()
        db.session.commit()
        return Status(200, "all recent prediction deleted").get()
    except:
        return Status(500, "Server error! Could not delete data").get()


@app.errorhandler(404)
def page_not_found(e):
    return render_template("pageNotFound.html")


if __name__ == "__main__":
    app.run(threaded=True, debug=True)