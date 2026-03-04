"""
This module takes care of starting the API Server,
Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

# ✅ Mejor configuración SQLite local
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://", "postgresql://"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# ---------------- ERROR HANDLER ----------------
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# ---------------- SITEMAP ----------------
@app.route("/")
def sitemap():
    return generate_sitemap(app)


# =====================================================
# PEOPLE
# =====================================================

@app.route("/people", methods=["GET"])
def get_people():
    all_people = Character.query.all()
    results = [person.serialize() for person in all_people]
    return jsonify(results), 200


@app.route("/people/<int:person_id>", methods=["GET"])
def get_single_people(person_id):
    person = Character.query.get(person_id)

    if person is None:
        return jsonify({"msg": "Character not found"}), 404

    return jsonify(person.serialize()), 200


@app.route("/people", methods=["POST"])
def create_person():
    body = request.get_json()

    if not body or "name" not in body:
        return jsonify({"msg": "Name is required"}), 400

    new_character = Character(
        name=body["name"],
        gender=body.get("gender"),
        height=body.get("height"),
        mass=body.get("mass"),
        hair_color=body.get("hair_color"),
        homeworld_id=body.get("homeworld_id")
    )

    db.session.add(new_character)
    db.session.commit()

    return jsonify(new_character.serialize()), 201


@app.route("/people/<int:person_id>", methods=["PUT"])
def update_person(person_id):
    person = Character.query.get(person_id)

    if person is None:
        return jsonify({"msg": "Character not found"}), 404

    body = request.get_json()

    if not body:
        return jsonify({"msg": "No data provided"}), 400

    if "name" in body:
        person.name = body["name"]

    if "gender" in body:
        person.gender = body["gender"]

    if "height" in body:
        person.height = body["height"]

    if "mass" in body:
        person.mass = body["mass"]

    if "hair_color" in body:
        person.hair_color = body["hair_color"]

    if "homeworld_id" in body:
        person.homeworld_id = body["homeworld_id"]

    db.session.commit()

    return jsonify(person.serialize()), 200


@app.route("/people/<int:person_id>", methods=["DELETE"])
def delete_person(person_id):
    person = Character.query.get(person_id)

    if person is None:
        return jsonify({"msg": "Character not found"}), 404

    db.session.delete(person)
    db.session.commit()

    return jsonify({"msg": "Character deleted"}), 200


# =====================================================
# PLANETS
# =====================================================

@app.route("/planets", methods=["GET"])
def get_planets():
    all_planets = Planet.query.all()
    results = [planet.serialize() for planet in all_planets]
    return jsonify(results), 200


@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    return jsonify(planet.serialize()), 200


# =====================================================
# FAVORITES (Simulated user_id = 1)
# =====================================================

@app.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    user = User.query.get(1)

    if user is None:
        return jsonify({"msg": "User not found"}), 404

    favorites = [fav.serialize() for fav in user.favorites]

    return jsonify(favorites), 200


@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    user = User.query.get(1)

    if user is None:
        return jsonify({"msg": "User not found"}), 404

    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    existing_favorite = Favorite.query.filter_by(
        user_id=user.id, planet_id=planet.id
    ).first()

    if existing_favorite:
        return jsonify({"msg": "Planet already in favorites"}), 400

    new_favorite = Favorite(
        user_id=user.id,
        planet_id=planet.id,
    )

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"msg": "Planet added to favorites"}), 201


@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    user = User.query.get(1)

    if user is None:
        return jsonify({"msg": "User not found"}), 404

    favorite = Favorite.query.filter_by(
        user_id=user.id, planet_id=planet_id
    ).first()

    if favorite is None:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Planet removed from favorites"}), 200


# =====================================================

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=True)