"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from http import HTTPStatus
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import Personaje, Planeta, Vehiculo, db, User
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = db.session.execute(db.select(User)).scalars().all()
        return jsonify([user.serialize() for user in users]), HTTPStatus.OK
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/personajes', methods=['GET'])
def get_personajes():
    try:
        personajes = db.session.execute(db.select(Personaje)).scalars().all()
        return jsonify([personaje.serialize() for personaje in personajes]), HTTPStatus.OK
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/personajes/<int:personaje_id>', methods=['GET'])
def get_single_person(personaje_id):
    try:
        personaje = db.session.execute(db.select(Personaje).where(
            Personaje.id == personaje_id)).scalar()
        if personaje is None:
            raise APIException("Personaje no encontrado",
                status_code=HTTPStatus.NOT_FOUND)
        return jsonify([personaje.serialize() for personaje in personaje]), HTTPStatus.OK
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/vehiculos', methods=['GET'])
def get_vehiculos():
    try:
        vehiculos = db.session.execute(db.select(Vehiculo)).scalars().all()
        return jsonify([vehiculo.serialize() for vehiculo in vehiculos]), HTTPStatus.OK
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/planetas', methods=['GET'])
def get_planetas():
    try:
        planetas = db.session.execute(db.select(Planeta)).scalars().all()
        return jsonify([planeta.serialize() for planeta in planetas]), HTTPStatus.OK
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)






# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
