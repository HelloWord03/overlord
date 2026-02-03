from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'overlord_secret_key_2026'


# CONFIGURACION IMÁGENES

UPLOAD_FOLDER = 'static/imagenes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#CONFIGURACION PATH BASE DE DATOS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'overlord.db')

if not os.path.exists(os.path.join(BASE_DIR, 'data')):
    os.makedirs(os.path.join(BASE_DIR, 'data'))

# CLASE PERSONAJE

class Personaje:
    def __init__(
        self, id=None, nombre='', raza='', clase='', nivel='', afiliacion='',
        descripcion='', karma='', creador='', ocupacion='',
        habilidades_especiales='', objeto_personal='', imagen=''
    ):
        self.id = id
        self.nombre = nombre
        self.raza = raza
        self.clase = clase
        self.nivel = nivel
        self.afiliacion = afiliacion
        self.descripcion = descripcion
        self.karma = karma
        self.creador = creador
        self.ocupacion = ocupacion
        self.habilidades_especiales = habilidades_especiales
        self.objeto_personal = objeto_personal
        self.imagen = imagen


# DATABASE PARA MANEJAR LA BASE DE DATOS

class Database:
    def __init__(self, db_name=DB_PATH):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                raza TEXT DEFAULT 'Desconocida',
                clase TEXT DEFAULT 'Desconocida',
                nivel TEXT DEFAULT 'Desconocido',
                afiliacion TEXT DEFAULT 'Desconocida',
                descripcion TEXT DEFAULT 'Información no disponible',
                karma TEXT DEFAULT 'Desconocido',
                creador TEXT DEFAULT 'Desconocido',
                ocupacion TEXT DEFAULT 'Sin ocupación',
                objeto_personal TEXT DEFAULT 'Sin posesiones',
                habilidades_especiales TEXT DEFAULT 'Sin habilidades',
                imagen TEXT DEFAULT 'nazarick.jpg'
            )
        ''')
        conn.commit()
        conn.close()

    def crear_personaje(self, p):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO personajes
            (nombre, raza, clase, nivel, afiliacion, descripcion,
             karma, creador, ocupacion, habilidades_especiales,
             objeto_personal, imagen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            p.nombre, p.raza, p.clase, p.nivel, p.afiliacion,
            p.descripcion, p.karma, p.creador, p.ocupacion,
            p.habilidades_especiales, p.objeto_personal, p.imagen
        ))
        conn.commit()
        conn.close()

    def obtener_todos(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM personajes ORDER BY nombre')
        rows = cursor.fetchall()
        conn.close()

        return [Personaje(**row) for row in rows]

    def obtener_por_id(self, id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM personajes WHERE id = ?', (id,))
        row = cursor.fetchone()
        conn.close()
        return Personaje(**row) if row else None

    def actualizar_personaje(self, p):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE personajes SET
                nombre=?, raza=?, clase=?, nivel=?, afiliacion=?,
                descripcion=?, karma=?, creador=?, ocupacion=?,
                habilidades_especiales=?, objeto_personal=?, imagen=?
            WHERE id=?
        ''', (
            p.nombre, p.raza, p.clase, p.nivel, p.afiliacion,
            p.descripcion, p.karma, p.creador, p.ocupacion,
            p.habilidades_especiales, p.objeto_personal,
            p.imagen, p.id
        ))
        conn.commit()
        conn.close()

    def eliminar_personaje(self, id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM personajes WHERE id = ?', (id,))
        conn.commit()
        conn.close()

db = Database()


# RUTAS

@app.route('/')
def index():
    personajes = db.obtener_todos()
    return render_template('index.html', personajes=personajes)

@app.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':

        imagen_path = None
        file = request.files.get('imagen')
        # Si hay una imagen y es válida, se guarda
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(ruta)
            imagen_path ='imagenes/' + filename
        else:
            #  Si no se sube imagen, se usa la predeterminada
            imagen_path = 'imagenes/nazarick.jpg'

        personaje = Personaje(
            nombre=request.form['nombre'].capitalize(),
            # Si request.form['raza'] es "", usará 'Desconocida'
            raza=request.form['raza'] or 'Desconocida',
            clase=request.form['clase'] or 'Desconocida',
            nivel=str(request.form['nivel']) or '0',
            afiliacion=request.form['afiliacion'] or 'Desconocida',
            descripcion=request.form['descripcion'] or 'Información no disponible',
            karma=request.form['karma'] or 'Desconocido',
            creador=request.form['creador'] or 'Desconocido',
            ocupacion=request.form['ocupacion'] or 'Sin ocupación',
            habilidades_especiales=request.form['habilidades_especiales'] or 'Sin habilidades',
            objeto_personal=request.form['objeto_personal'] or 'Sin posesiones',
            imagen=imagen_path 
        )

        db.crear_personaje(personaje)
        flash('¡Personaje creado exitosamente!', 'success')
        return redirect(url_for('index'))

    return render_template('crear.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    personaje = db.obtener_por_id(id)
    if not personaje:
        flash('Personaje no encontrado', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        personaje.nombre = request.form['nombre']
        personaje.raza = request.form['raza'] or 'Desconocida'
        personaje.clase = request.form['clase'] or 'Desconocida'
        personaje.nivel = str(request.form['nivel']) 
        personaje.afiliacion = request.form['afiliacion'] or 'Desconocida'
        personaje.descripcion = request.form['descripcion'] or 'Información no disponible'
        personaje.karma = request.form['karma'] or 'Desconocido'
        personaje.creador = request.form['creador'] or 'Desconocido'
        personaje.ocupacion = request.form['ocupacion'] or 'Sin ocupación'
        personaje.habilidades_especiales = request.form['habilidades_especiales'] or 'Sin habilidades'
        personaje.objeto_personal = request.form['objeto_personal'] or 'Sin posesiones'
        file = request.files.get('imagen')
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(ruta)
            personaje.imagen = 'imagenes/' + filename

        db.actualizar_personaje(personaje)
        flash('¡Personaje actualizado exitosamente!', 'success')
        return redirect(url_for('index'))

    return render_template('editar.html', personaje=personaje)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db.eliminar_personaje(id)
    flash('¡Personaje eliminado exitosamente!', 'success')
    return redirect(url_for('index'))

@app.route('/ver/<int:id>')
def ver(id):
    personaje = db.obtener_por_id(id)
    if not personaje:
        flash('Personaje no encontrado', 'error')
        return redirect(url_for('index'))
    return render_template('ver.html', personaje=personaje)


# SACAR IMÁGENES

@app.route('/imagenes/<path:filename>')
def imagenes(filename):
    return send_from_directory('static/imagenes', filename)

if __name__ == '__main__':
    app.run(debug=True)
