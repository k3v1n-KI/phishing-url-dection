from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from phishing_model import Model
from flask_cors import CORS

app = Flask(__name__)  
api = Api(app)
CORS(app)

model_args = reqparse.RequestParser()
model_args.add_argument("url", type=str, help="URL for model inference", required=True)
model = Model()

class ModelApi(Resource):
    def get(self):
        return {"Yoo": "Yoo"}
    
    def put(self, url_id):
        args = model_args.parse_args()
        if not args['url']:
            return jsonify({"error": "URL is required"}), 400
        prediction = model.predict_phishing_url(args["url"])
        return jsonify({url_id: prediction})

api.add_resource(ModelApi, "/model/<int:url_id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
