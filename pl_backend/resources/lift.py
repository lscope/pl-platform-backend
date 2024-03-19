from flask_restful import Resource
from flask import request



class LiftResource(Resource):
    def get(self, user_id, lift_type):
        return {"message": f"Returned {lift_type} for user {user_id}"}

    def post(self, user_id, lift_type):
        data = request.get_json()
        weight = data.get("weight")

        return {"message": f"Added {weight}kg {lift_type} for user {user_id}"}
