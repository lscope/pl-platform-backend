from flask_restful import Resource



class UserResource(Resource):
    def get(self, user_id):
        return {"message": f"Hi user {user_id}"}

    def post(self):
        return {"message": f"Created user"}

    def delete(self, user_id):
        return {"message": f"Deleted user {user_id}"}
