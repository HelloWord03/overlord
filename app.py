from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, make_response
import csv
import io
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os


# CONFIGURACIÓN DE LA APP

app = Flask(__name__)
app.secret_key = 'overlord_secret_key_2026'

UPLOAD_FOLDER = 'static/imagenes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Base de datos con SQLAlchemy
# Obtener la carpeta donde reside el script actual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'overlord.db')
if not os.path.exists(os.path.join(BASE_DIR, 'data')):
    os.makedirs(os.path.join(BASE_DIR, 'data'))

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



# MODELO DE DATOS

class Personaje(db.Model):
    __tablename__ = 'personajes' # Forzamos el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    raza = db.Column(db.String(100))
    clase = db.Column(db.String(100))
    nivel = db.Column(db.String(50), default='Desconocido')
    afiliacion = db.Column(db.String(100))
    descripcion = db.Column(db.Text, default='Información no disponible')
    karma = db.Column(db.String(50), default='Desconocido')
    creador = db.Column(db.String(100), default='Desconocido')
    ocupacion = db.Column(db.String(100), default='Sin ocupación')
    habilidades_especiales = db.Column(db.Text, default='Sin habilidades')
    objeto_personal = db.Column(db.String(200), default='Sin posesiones')
    imagen = db.Column(db.String(300), default='imagenes/nazarick.jpg')

    def __repr__(self):
        return f"<Personaje {self.nombre}>"


# Crear la base de datos si no existe
with app.app_context():
    db.create_all()



# FUNCIONES AUXILIARES

def allowed_file(filename):
    """
    Verifica si un archivo tiene extensión permitida.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# RUTAS

@app.route('/')
def index():
    """
    Página principal: lista todos los personajes.
    """
    personajes = Personaje.query.order_by(Personaje.nombre).all()
    return render_template('index.html', personajes=personajes)


@app.route('/crear', methods=['GET', 'POST'])
def crear():
    """
    Crear un nuevo personaje desde un formulario.
    """
    if request.method == 'POST':
        file = request.files.get('imagen')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(ruta)
            imagen_path = 'imagenes/' + filename
        else:
            imagen_path = 'imagenes/nazarick.jpg'

        # Usamos .strip() y 'or' para forzar los valores por defecto si el campo está vacío
        personaje = Personaje(
            nombre=request.form['nombre'].capitalize(),
            raza=request.form.get('raza', '').strip() or 'Desconocida',
            clase=request.form.get('clase', '').strip() or 'Desconocida',
            nivel=request.form.get('nivel', '').strip() or 'Desconocido',
            afiliacion=request.form.get('afiliacion', '').strip() or 'Desconocida',
            descripcion=request.form.get('descripcion', '').strip() or 'Información no disponible',
            karma=request.form.get('karma', '').strip() or 'Desconocido',
            creador=request.form.get('creador', '').strip() or 'Desconocido',
            ocupacion=request.form.get('ocupacion', '').strip() or 'Sin ocupación',
            habilidades_especiales=request.form.get('habilidades_especiales', '').strip() or 'Sin habilidades',
            objeto_personal=request.form.get('objeto_personal', '').strip() or 'Sin posesiones',
            imagen=imagen_path
        )

        db.session.add(personaje)
        db.session.commit()
        flash('¡Personaje creado exitosamente!', 'success')
        return redirect(url_for('index'))

    return render_template('crear.html')


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """
    Editar un personaje existente.
    """
    personaje = Personaje.query.get_or_404(id)

    if request.method == 'POST':
        personaje.nombre = request.form['nombre'].strip().capitalize()
        personaje.raza = request.form.get('raza', '').strip() or 'Desconocida'
        personaje.clase = request.form.get('clase', '').strip() or 'Desconocida'
        personaje.nivel = request.form.get('nivel', '').strip() or 'Desconocido'
        personaje.afiliacion = request.form.get('afiliacion', '').strip() or 'Desconocida'
        personaje.descripcion = request.form.get('descripcion', '').strip() or 'Información no disponible'
        personaje.karma = request.form.get('karma', '').strip() or 'Desconocido'
        personaje.creador = request.form.get('creador', '').strip() or 'Desconocido'
        personaje.ocupacion = request.form.get('ocupacion', '').strip() or 'Sin ocupación'
        personaje.habilidades_especiales = request.form.get('habilidades_especiales', '').strip() or 'Sin habilidades'
        personaje.objeto_personal = request.form.get('objeto_personal', '').strip() or 'Sin posesiones'

        file = request.files.get('imagen')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(ruta)
            personaje.imagen = 'imagenes/' + filename

        db.session.commit()
        flash('¡Personaje actualizado exitosamente!', 'success')
        return redirect(url_for('index'))

    return render_template('editar.html', personaje=personaje)


@app.route('/eliminar/<int:id>')
def eliminar(id):
    """
    Elimina un personaje por su ID.
    """
    personaje = Personaje.query.get_or_404(id)
    
    # Necesitamos apuntar a 'static/imagenes/foto.jpg'
    if personaje.imagen and personaje.imagen != 'imagenes/nazarick.jpg':
        # Construimos la ruta: static/ + imagenes/nombre.jpg
        ruta_imagen = os.path.join('static', personaje.imagen)
        
        # 2. Verificar si el archivo existe y borrarlo
        if os.path.exists(ruta_imagen):
            try:
                os.remove(ruta_imagen)
            except Exception as e:
                print(f"Error al eliminar el archivo físico: {e}")
                
    db.session.delete(personaje)
    db.session.commit()
    flash('¡Personaje eliminado exitosamente!', 'success')
    return redirect(url_for('index'))


@app.route('/ver/<int:id>')
def ver(id):
    """
    Visualiza los detalles de un personaje.
    """
    personaje = Personaje.query.get_or_404(id)
    return render_template('ver.html', personaje=personaje)


@app.route('/imagenes/<path:filename>')
def imagenes(filename):
    """
    Devuelve imágenes desde la carpeta estática.
    """
    return send_from_directory('static', filename)


@app.route('/descargar_csv')
def descargar_csv():
    """
    Genera y descarga un archivo CSV con todos los personajes.
    """
    # Obtener todos los personajes de la base de datos
    personajes = Personaje.query.order_by(Personaje.nombre).all()

    # Crear un buffer en memoria para el CSV
    si = io.StringIO()
    cw = csv.writer(si)

    # Definir los encabezados (las columnas del CSV)
    cw.writerow([
        'ID', 'Nombre', 'Raza', 'Clase', 'Nivel', 'Afiliación', 
        'Descripción', 'Karma', 'Creador', 'Ocupación', 
        'Habilidades Especiales', 'Objeto Personal', 'Imagen'
    ])

    # Agregar los datos de cada personaje
    for p in personajes:
        cw.writerow([
            p.id, p.nombre, p.raza, p.clase, p.nivel, p.afiliacion,
            p.descripcion, p.karma, p.creador, p.ocupacion,
            p.habilidades_especiales, p.objeto_personal, p.imagen
        ])

    # Crear la respuesta de descarga
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=personajes_overlord.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output

@app.route('/descargar_csv/<int:id>')
def descargar_csv_personaje(id):
    """
    Genera y descarga un archivo CSV con el personaje seleccinado.
    """
    # Obtener el personaje de la base de datos
    personaje = Personaje.query.get_or_404(id)

    # Crear un buffer en memoria para el CSV
    si = io.StringIO()
    cw = csv.writer(si)

    # Definir los encabezados (las columnas del CSV)
    cw.writerow([
        'ID', 'Nombre', 'Raza', 'Clase', 'Nivel', 'Afiliación', 
        'Descripción', 'Karma', 'Creador', 'Ocupación', 
        'Habilidades Especiales', 'Objeto Personal', 'Imagen'
    ])

    #Variable para el nombre del archivo (limpiamos espacios y pasamos a minúsculas)
    fileNombre =personaje.nombre.replace(" ","_").lower()
    # Agregar los datos del personaje
    cw.writerow([
        personaje.id, personaje.nombre, personaje.raza, personaje.clase, personaje.nivel, personaje.afiliacion,
        personaje.descripcion, personaje.karma, personaje.creador, personaje.ocupacion,
        personaje.habilidades_especiales, personaje.objeto_personal, personaje.imagen
    ])


    # Crear la respuesta de descarga 
    # Aquí usamos f"..." para que reconozca {fileNombre}
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={fileNombre}.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output

# EJECUCIÓN DE LA APP

if __name__ == '__main__':
    app.run(debug=True)
