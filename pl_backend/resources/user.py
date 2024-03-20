from flask_restful import Resource
from flask import request, jsonify
from marshmallow import Schema, fields, ValidationError
from ..models.user import User
from ..models import db


# Schema per validare il JSON della richiest POST
class UserSchema(Schema):
    first_name = fields.Str(required=True, data_key="firstName") # Cerca la chiave data_key
    last_name = fields.Str(required=True, data_key="lastName")

class UserResource(Resource):
    def get(self, user_id):
        user = User.query.filter(User.id == user_id).first() # Filtro l'utente. Se non esiste restituisce None

        # Se non ho trovato l'utente, restituisco un messaggio esplicativo e status code 404
        if user is None:
            return {"message": "User not found"}, 404

        return {
            "message": "User found",
            "data": user.to_json(),
        }

    def post(self):
        try:
            # Recupero i dati della richiesta, facendo un controllo sulla struttura
            data = UserSchema().load(request.get_json()) # Se è tutto ok restituisce il json avente come chiavi le variabili python definite nello schema
        except ValidationError as e:
            # Restituisce un errore se la validazione fallisce
            return {
                "message": str(e),
            }, 400

        first_name = data.get("first_name")
        last_name = data.get("last_name")

        # Creo il nuovo utente da aggiungere
        user = User(
            first_name=first_name,
            last_name=last_name,
        )

        # Aggiungo l'utente
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            # Se c'è un qualsiasi errore faccio il rollback della sessione e restituisco l'errore
            db.session.rollback()

            return {
                "message": "Failed to create user",
                "error": str(e),
            }, 500

        return {
            "message": "New user created",
            "data": user.to_json(),
        }, 201

    def delete(self, user_id):
        user = User.query.filter(User.id == user_id).first()

        if user is not None:
            try:
                db.session.delete(user)
                db.session.commit()
            except Exception as e:
                db.session.rollback()

                return {
                    "message": "Failed to delete user",
                    "error": str(e),
                }, 500

        return {"message": f"Deleted user {user_id}"}
