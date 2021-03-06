from flask import Flask, jsonify, request, json, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import true
from flask_cors import CORS
from datetime import datetime, timedelta
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
    starred = db.Column(db.Boolean, default=False)
    tags = db.Column(db.Text, default="")

    def __str__(self):
        return f"Prediction(id={self.id}, date-created={self.createdAt}, result={self.outcome}, user-input={self.inputs}), starred={self.starred}, tags={self.tags}"


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


@app.route('/api/recent/<int:id>')
def getRecentById(id):
    try:
        obj = Prediction.query.get(id)
        return jsonify(object_serializer(obj))
    except:
        return Status(500, "Server error! Could not get data").get()


@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        model = Model()
        request_data = json.loads(request.data)
        converted_data = convert_for_model(request_data)
        predicted = model.predict_result(converted_data)[0]
        return str(float("{:.4f}".format(predicted)))
    except:
        return Status(400, "Failed to compute result with given inputs").get()


@app.route('/api/save', methods=["POST"])
def save_predicted():
    try:
        request_data = json.loads(request.data)
        dateObj = datetime.fromisoformat(request_data['createdAt'])
        res = Prediction(createdAt=dateObj,
                         outcome=json.dumps(request_data['outcome']),
                         inputs=json.dumps(request_data['inputs']),
                         tags=request_data['tags'])
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


@app.route('/api/update/<int:id>', methods=['PATCH'])
def starResult(id):
    try:
        prevState = object_serializer(Prediction.query.get(id))["starred"]
        Prediction.query.filter_by(id=id).update(dict(starred=(not prevState)))
        db.session.commit()
        return Status(200, "recent prediction updated").get()
    except:
        return Status(500, "Server error! Could not update data").get()


@app.route('/api/search', methods=['GET'])
def searchRecent():
    try:
        tag = request.args.get('tag')
        status = request.args.get('status')
        starred = request.args.get('starred')
        recent = request.args.get('recent')
        tags_query = starred_query = status_query = recent_query = true()
        if tag:
            tags_query = Prediction.tags.contains(tag)

        if status:
            status_query = Prediction.outcome.contains(status)

        if starred:
            starred = True if starred == 'true' else False
            starred_query = Prediction.starred == starred

        if recent:
            now = datetime.now() + timedelta(hours=5, minutes=30)
            recent_query = (now - timedelta(days=int(recent)) <=
                            Prediction.createdAt)

        searchResult = Prediction.query.filter((tags_query & starred_query
                                                & status_query & recent_query))
        return jsonify([*map(object_serializer, searchResult)])
    except:
        return Status(500, "Server error! Could not get data").get()


@app.errorhandler(404)
def page_not_found(e):
    return render_template("pageNotFound.html")


if __name__ == "__main__":
    app.run(threaded=True, debug=True)