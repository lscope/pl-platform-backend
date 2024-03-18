from flask_restful import Resource



class UserResource(Resource):
    def get(self):
        return {"message": f"Hi user"}

    def post(self):
        return {"message": f"Created user"}

    def delete(self):
        return {"message": f"Deleted user"}
