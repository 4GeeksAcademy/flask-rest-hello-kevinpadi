"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Favorite, Vehicle, Character
from sqlalchemy import and_

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#endpoints
#get all users
@app.route('/user', methods=['GET'])
def get_users():
    try:
        results_query = User.query.all()
        results = list(map(lambda item: item.serialize(), results_query))
        response_body = {
            "msg": "Ok",
            "results": results
        }
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#get user by id
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    try:
        results_query = User.query.filter_by(id=id).first()
        if results_query:
            response_body = {
            "msg": "Ok",
            "results": results_query.serialize()
            }
            return jsonify(response_body), 200
        return jsonify({"msg": "No existe ese usuario"}), 400
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@app.route('/planet', methods=['GET'])#SEGUIR TESTEANDO
def get_planets():
    try:
        results_query = Planet.query.all()
        results = list(map(lambda item: item.serialize(), results_query))
        response_body = {
            "msg": "Ok",
            "results": results
        }
        if results_query:
            return jsonify(response_body), 200
        return jsonify({"msg": "No hay planetas"}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#get Planet by planet_id
@app.route('/planet/<int:id>', methods=['GET'])
def get_planet(id):
    try:
        results_query = Planet.query.filter_by(id=id).first()
        if results_query:
            response_body = {
                "msg": "Ok",
                "results": results_query.serialize()
            }
            return jsonify(response_body), 200
        return jsonify({"msg": "No existe este planeta"}), 404
    except Exception as e:
            return jsonify({"msg": str(e)}), 500

@app.route('/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user:
            return jsonify({"msg": "Email already exists"}), 400
        user_created = User(name=data["name"], email=data["email"], password=data["password"], is_active=data["is_active"])
        db.session.add(user_created)
        db.session.commit()
        response_body = {
            "msg": "User created successfully",
        }
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#Characters/People
@app.route('/character', methods=['GET'])
def get_characters():
    try:
        results_query = Character.query.all()
        results = list(map(lambda item: item.serialize(), results_query))
        print(results)
        response_body = {
            "msg": "Ok",
            "results": results
        }
        if results_query:
            return jsonify(response_body), 200
        return jsonify({"msg": "No existen personajes"}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#GET CHARACTER BY ID
@app.route('/character/<int:id>', methods=['GET'])
def get_character(id):
    try:
        results_query = Character.query.filter_by(id=id).first()
        if results_query: 
            response_body = {
                "msg": "Ok",
                "results": results_query.serialize()
            }
            return jsonify(response_body), 200
        return jsonify({"msg": "Personaje no encontrado"}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#GET FAVORITES BY USER ID
@app.route('/users/<int:id>/favorites', methods=['GET'])
def get_favorites(id):
    try:
        results_query = Favorite.query.filter_by(user_id=id).all()
        if results_query:
            results = list(map(lambda item: item.serialize(), results_query))
            response_body = {
                "msg": "Ok",
                "results": results
            }
            return jsonify(response_body), 200
        return jsonify({"msg": "No hay favoritos para este usuario."}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#AGREGAR PLANETA FAVORITO
@app.route('/users/<int:user_id>/favorites/planet/<int:planet_id>', methods=['POST'])
def create_favorite_planet(user_id, planet_id):
    try:
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            return jsonify({"msg": "El usuario no existe"}), 400
        planet_exists = Planet.query.filter_by(id=planet_id).first()
        if not planet_exists:
            return jsonify({"msg": "El planeta no existe"}), 400

        existing_favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
        if existing_favorite:
            return jsonify({"msg": "El favorito ya existe"}), 400

        favorite_created = Favorite(user_id=user_id, planet_id=planet_id)
        db.session.add(favorite_created)
        db.session.commit()

        response_body = {
            "msg": "Favorito creado",
            "favorito": favorite_created.serialize()
        }
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@app.route('/users/<int:user_id>/favorites/character/<int:character_id>', methods=['POST'])
def create_favorite_character(user_id, character_id):
    try:
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            return jsonify({"msg": "El usuario no existe"}), 400
        character_exists = Character.query.filter_by(id=character_id).first()
        if not character_exists:
            return jsonify({"msg": "El character no existe"}), 400

        existing_favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
        if existing_favorite:
            return jsonify({"msg": "El favorito ya existe"}), 400

        favorite_created = Favorite(user_id=user_id, character_id=character_id)
        db.session.add(favorite_created)
        db.session.commit()

        response_body = {
            "msg": "Favorito creado",
            "favorito": favorite_created.serialize()
        }
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#DELETE PLANET FROM FAVORITES
@app.route('/users/<int:user_id>/favorites/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    try:
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            return jsonify({"msg": "El usuario no existe"}), 400
        planet_exists = Planet.query.filter_by(id=planet_id).first()
        if not planet_exists:
            return jsonify({"msg": "El planeta no existe"}), 400
        existing_favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
        if existing_favorite:
            db.session.delete(existing_favorite)
            db.session.commit()
            return jsonify({"msg": "El favorito fue eliminado"}), 200
        return jsonify({"msg": "No existe ese favorito, no se pudo eliminar"}), 400
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

#DELETE character FROM FAVORITES
@app.route('/users/<int:user_id>/favorites/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(user_id, character_id):
    try:
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            return jsonify({"msg": "El usuario no existe"}), 400
        character_exists = Character.query.filter_by(id=character_id).first()
        if not character_exists:
            return jsonify({"msg": "El character no existe"}), 400
        existing_favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
        if existing_favorite:
            db.session.delete(existing_favorite)
            db.session.commit()
            return jsonify({"msg": "El favorito fue eliminado"}), 200
        return jsonify({"msg": "Ese favorito no existe, no se pudo eliminar"}), 400
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
