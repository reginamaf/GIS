from flask_restful import Resource

class vcr(Resource):
    def get(self):
         return {"filename": "name",
                "cover": "coverage",
                "area": "areaRange",
                "centroid" : "centroidLoc",
                "local_time": "time"}