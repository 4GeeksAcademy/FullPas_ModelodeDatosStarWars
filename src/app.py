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

######################################################################################################################
@app.route('/')
def sitemap():
    return generate_sitemap(app)

######################################################################################################################
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = db.session.execute(db.select(User)).scalars().all()
        return jsonify([user.serialize() for user in users]), HTTPStatus.OK
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

######################################################################################################################
@app.route('/personajes', methods=['GET'])
def get_personajes():
    try:
        personajes = db.session.execute(db.select(Personaje)).scalars().all()
        return jsonify([personaje.serialize() for personaje in personajes]), HTTPStatus.OK
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def get_personaje_by_id(personaje_id):
    personaje = db.session.execute(
        db.select(Personaje).where(Personaje.id == personaje_id)
    ).scalar_one_or_none()

    if personaje is None:
        raise APIException(
            "Personaje no encontrado",
            status_code=HTTPStatus.NOT_FOUND
        )

    return personaje

@app.route('/personajes/<int:personaje_id>', methods=['GET'])
def get_single_person(personaje_id):
    try:
        personaje = get_personaje_by_id(personaje_id)
        return jsonify(personaje.serialize()), HTTPStatus.OK
    except APIException:
        raise
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )
######################################################################################################################

@app.route('/vehiculos', methods=['GET'])
def get_vehiculos():
    try:
        vehiculos = db.session.execute(db.select(Vehiculo)).scalars().all()
        return jsonify([vehiculo.serialize() for vehiculo in vehiculos]), HTTPStatus.OK
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

######################################################################################################################
@app.route('/planetas', methods=['GET'])
def get_planetas():
    try:
        planetas = db.session.execute(db.select(Planeta)).scalars().all()
        return jsonify([planeta.serialize() for planeta in planetas]), HTTPStatus.OK
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def get_planeta_by_id(planeta_id):
    planeta = db.session.execute(
        db.select(Planeta).where(Planeta.id == planeta_id)
    ).scalar_one_or_none()

    if planeta is None:
        raise APIException(
            "Planeta no encontrado",
            status_code=HTTPStatus.NOT_FOUND
        )

    return planeta

######################################################################################################################
def get_current_user():
    user_id = request.args.get('user_id', type=int)

    if user_id is None:
        user_id_header = request.headers.get('User-Id')
        if user_id_header is not None:
            try:
                user_id = int(user_id_header)
            except ValueError:
                user_id = None

    if user_id is None and request.is_json:
        payload = request.get_json(silent=True) or {}
        user_id = payload.get('user_id')

    if user_id is not None:
        user = db.session.get(User, user_id)
    else:
        user = db.session.execute(
            db.select(User).order_by(User.id)
        ).scalar_one_or_none()

    if user is None:
        user = User(
            email='current_user@example.com',
            password='test',
            tipo='usuario',
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

    return user

######################################################################################################################
@app.route('/planetas/<int:planeta_id>', methods=['GET'])
def get_single_planeta(planeta_id):
    try:
        planeta = get_planeta_by_id(planeta_id)
        return jsonify(planeta.serialize()), HTTPStatus.OK
    except APIException:
        raise
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

######################################################################################################################
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    try:
        current_user = get_current_user()
        return jsonify({
            'personajes': [personaje.serialize() for personaje in current_user.personajes_favoritos],
            'vehiculos': [vehiculo.serialize() for vehiculo in current_user.vehiculos_favoritos],
            'planetas': [planeta.serialize() for planeta in current_user.planetas_favoritos]
        }), HTTPStatus.OK
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

######################################################################################################################
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    try:
        current_user = get_current_user()
        planeta = get_planeta_by_id(planet_id)

        if planeta in current_user.planetas_favoritos:
            raise APIException(
                'Planeta ya está en favoritos',
                status_code=HTTPStatus.CONFLICT
            )

        current_user.planetas_favoritos.append(planeta)
        db.session.commit()
        return jsonify({'message': 'Planeta añadido a favoritos'}), HTTPStatus.CREATED
    except APIException:
        raise
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

######################################################################################################################
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    try:
        current_user = get_current_user()
        personaje = get_personaje_by_id(people_id)

        if personaje in current_user.personajes_favoritos:
            raise APIException(
                'Personaje ya está en favoritos',
                status_code=HTTPStatus.CONFLICT
            )

        current_user.personajes_favoritos.append(personaje)
        db.session.commit()
        return jsonify({'message': 'Personaje añadido a favoritos'}), HTTPStatus.CREATED
    except APIException:
        raise
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    try:
        current_user = get_current_user()
        planeta = get_planeta_by_id(planet_id)

        if planeta not in current_user.planetas_favoritos:
            raise APIException(
                'Planeta no encontrado en favoritos',
                status_code=HTTPStatus.NOT_FOUND
            )

        current_user.planetas_favoritos.remove(planeta)
        db.session.commit()
        return jsonify({'message': 'Planeta eliminado de favoritos'}), HTTPStatus.OK
    except APIException:
        raise
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    try:
        current_user = get_current_user()
        personaje = get_personaje_by_id(people_id)

        if personaje not in current_user.personajes_favoritos:
            raise APIException(
                'Personaje no encontrado en favoritos',
                status_code=HTTPStatus.NOT_FOUND
            )

        current_user.personajes_favoritos.remove(personaje)
        db.session.commit()
        return jsonify({'message': 'Personaje eliminado de favoritos'}), HTTPStatus.OK
    except APIException:
        raise
    except Exception as e:
        raise APIException(
            str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

######################################################################################################################
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
