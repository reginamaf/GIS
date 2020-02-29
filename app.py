from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_restful import Api
from models.vegetation_cover_result import VegetationCoverResult

app = Flask(__name__)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name':"Strider GIS Challenge API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

api = Api(app)

api.add_resource(VegetationCoverResult, '/vegetation-cover')

if __name__ == "__main__":
    app.run(debug=True)

