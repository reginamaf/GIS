from flask import Flask
from flask_restful import Api
from resources.vegetationCoverResult import vcr

app = Flask(__name__)
api = Api(app)

api.add_resource(vcr, '/vegetation-cover')

if __name__ == "__main__":
    app.run(debug=True)

