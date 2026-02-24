from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ---------------- USER ----------------
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    subscription_date = db.Column(db.Date)

    favorites = db.relationship("Favorite", backref="user", lazy=True)


# ---------------- PLANET ----------------
class Planet(db.Model):
    __tablename__ = "planet"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    population = db.Column(db.String(120))
    terrain = db.Column(db.String(120))
    climate = db.Column(db.String(120))

    residents = db.relationship("Character", backref="homeworld", lazy=True)


# ---------------- CHARACTER ----------------
class Character(db.Model):
    __tablename__ = "character"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    height = db.Column(db.String(50))
    mass = db.Column(db.String(50))
    gender = db.Column(db.String(50))

    homeworld_id = db.Column(db.Integer, db.ForeignKey("planet.id"))


# ---------------- FAVORITE ----------------
class Favorite(db.Model):
    __tablename__ = "favorite"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"))
    character_id = db.Column(db.Integer, db.ForeignKey("character.id"))