import json
import argparse
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configuración mínima de Flask para que SQLAlchemy funcione
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
db_path = os.path.join(basedir, "data", "overlord.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DE LA BASE DE DATOS ---
class Personaje(db.Model):
    __tablename__ = 'personajes' # Forzamos el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    raza = db.Column(db.String(100), default='Desconocida')
    clase = db.Column(db.String(100), default='Desconocida')
    nivel = db.Column(db.String(50), default='Desconocido')
    afiliacion = db.Column(db.String(100), default='Desconocida')
    descripcion = db.Column(db.Text, default='Información no disponible')
    karma = db.Column(db.String(50), default='Desconocido')
    creador = db.Column(db.String(100), default='Desconocido')
    ocupacion = db.Column(db.String(100), default='Sin ocupación')
    habilidades_especiales = db.Column(db.Text, default='Sin habilidades')
    objeto_personal = db.Column(db.String(200), default='Sin posesiones')
    imagen = db.Column(db.String(300), default='imagenes/nazarick.jpg')

    def __repr__(self):
        return f"<Personaje {self.nombre}>"

def insertar_personajes_desde_json(archivo_json, limpiar_tabla=False):
    """Inserta personajes en la base de datos desde un archivo JSON.
    Args:
        archivo_json (str): Ruta al archivo JSON con los datos de los personajes.
        limpiar_tabla (bool): Si es True, limpia la tabla antes de insertar nuevos datos.
    """
    if not os.path.exists(archivo_json):
        print(f"Error: No se encuentra el archivo {archivo_json}")
        return

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

        if limpiar_tabla:
            Personaje.query.delete()
            print("Tabla limpiada. Todos los registros anteriores fueron eliminados.\n")

        try:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
            return

        personajes_insertados = 0
        for i, p in enumerate(datos.get('personajes', []), 1):
            try:
                nuevo_personaje = Personaje(
                    nombre=p.get('nombre', ''),
                    raza=p.get('raza', 'Desconocida'),
                    clase=p.get('clase', 'Desconocida'),
                    nivel=str(p.get('nivel', 'Desconocido')),
                    afiliacion=p.get('afiliacion', 'Desconocida'),
                    descripcion=p.get('descripcion', 'Información no disponible'),
                    karma=str(p.get('karma', 'Desconocido')),
                    creador=p.get('creador', 'Desconocido'),
                    ocupacion=p.get('ocupacion', 'Sin ocupación'),
                    habilidades_especiales=p.get('habilidades_especiales', 'Sin habilidades'),
                    objeto_personal=p.get('objeto_personal', 'Sin posesiones'),
                    imagen=p.get('imagen', 'Sin imagen')
                )
                db.session.add(nuevo_personaje)
                personajes_insertados += 1
                print(f"[{i}] Preparado: {p.get('nombre')}")
            except Exception as e:
                print(f"[{i}] Error con {p.get('nombre')}: {e}")

        db.session.commit()
        print(f"\nResumen: {personajes_insertados} personajes guardados en {app.config['SQLALCHEMY_DATABASE_URI']}")

def main():
    """Función principal para manejar argumentos y ejecutar la inserción."""
    
    parser = argparse.ArgumentParser(description='Insertar personajes usando SQLAlchemy')
    parser.add_argument('archivo_json', nargs='?', default='./data/personajes.json')
    parser.add_argument('--limpiar', action='store_true')
    args = parser.parse_args()

    if args.limpiar:
        if input("¿Eliminar todo? (s/N): ").lower() == 's':
            insertar_personajes_desde_json(args.archivo_json, True)
    else:
        insertar_personajes_desde_json(args.archivo_json)

if __name__ == "__main__":
    main()