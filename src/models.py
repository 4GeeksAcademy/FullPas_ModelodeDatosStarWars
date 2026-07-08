from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favoritos_personajes: Mapped[List["Fav_Personajes"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    
class Personajes(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    raza: Mapped[str] = mapped_column(nullable=False)
    nacimiento: Mapped[str] = mapped_column(nullable=False)
    color_ojos: Mapped[str] = mapped_column(nullable=False)

    favoritos_personajes: Mapped[List["Fav_Personajes"]] = relationship(back_populates="personaje")


class Fav_Personajes(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    user: Mapped["User"] = relationship(back_populates="favoritos_personajes")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    personaje: Mapped["Personajes"] = relationship(back_populates="favoritos_personajes")
    personaje_id: Mapped[int] = mapped_column(ForeignKey("personajes.id"))
                                        


class Vehiculos(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(nullable=False)
    tamaño: Mapped[str] = mapped_column(nullable=False)

    favoritos_vehiculos: Mapped[List["Fav_Vehiculos"]] = relationship(back_populates="vehiculo")


class Fav_Vehiculos(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    user: Mapped["User"] = relationship(back_populates="favoritos_vehiculos")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    vehiculo: Mapped["Personajes"] = relationship(back_populates="favoritos_personajes")
    vehiculo_id: Mapped[int] = mapped_column(ForeignKey("vehiculos.id"))


class Planetas(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(nullable=False)
    tamaño: Mapped[str] = mapped_column(nullable=False)
    poblacion: Mapped[int] = mapped_column(nullable=False)

    favoritos_planetas: Mapped[List["Fav_Planetas"]] = relationship(back_populates="planeta")


class Fav_Planetas(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    user: Mapped["User"] = relationship(back_populates="favoritos_planetas")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    planeta: Mapped["Planetas"] = relationship(back_populates="favoritos_planetas")
    planeta_id: Mapped[int] = mapped_column(ForeignKey("planetas.id"))
