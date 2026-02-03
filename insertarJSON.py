import sqlite3
import json
import argparse
import os

def insertar_personajes_desde_json(archivo_json, db_path='./data/overlord.db', limpiar_tabla=False):
    """
    Lee un archivo JSON con personajes y los inserta en la base de datos SQLite.
    
    Args:
        archivo_json: Ruta al archivo JSON con los personajes
        db_path: Ruta a la base de datos SQLite (por defecto './data/overlord.db')
        limpiar_tabla: Si es True, elimina todos los registros antes de insertar (por defecto False)
    """
    
    # Verificar que existe el archivo JSON
    if not os.path.exists(archivo_json):
        print(f"Error: No se encuentra el archivo {archivo_json}")
        return
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear la tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            raza TEXT NOT NULL,
            clase TEXT NOT NULL,
            nivel TEXT NOT NULL,
            afiliacion TEXT NOT NULL,
            descripcion TEXT,
            karma TEXT,
            creador TEXT,
            ocupacion TEXT,
            objeto_personal TEXT,
            habilidades_especiales TEXT,
            imagen TEXT
        )
    ''')
    
    # Limpiar tabla si se solicita
    if limpiar_tabla:
        cursor.execute('DELETE FROM personajes')
        print("Tabla limpiada. Todos los registros anteriores fueron eliminados.\n")
    
    # Leer el archivo JSON
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error al leer el archivo JSON: {e}")
        conn.close()
        return
    except Exception as e:
        print(f"Error inesperado al leer el archivo: {e}")
        conn.close()
        return
    
    # Verificar que existe la clave 'personajes'
    if 'personajes' not in datos:
        print("Error: El archivo JSON no contiene la clave 'personajes'")
        conn.close()
        return
    
    # Insertar cada personaje
    personajes_insertados = 0
    personajes_con_error = 0
    
    for i, personaje in enumerate(datos['personajes'], 1):
        try:
            cursor.execute('''
                INSERT INTO personajes (
                    nombre, raza, clase, nivel, afiliacion, descripcion,
                    karma, creador, ocupacion, habilidades_especiales,
                    objeto_personal, imagen
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                personaje.get('nombre', ''),
                personaje.get('raza', 'Desconocida'),
                personaje.get('clase', 'Desconocida'),
                str(personaje.get('nivel', 'Desconocido')), # Convertir a int por si es número
                personaje.get('afiliacion', 'Desconocida'),
                personaje.get('descripcion', 'Información no disponible'),
                str(personaje.get('karma', 'Desconocido')),  # Convertir a string por si es número
                personaje.get('creador', 'Desconocido'),
                personaje.get('ocupacion', 'Sin ocupación'),
                personaje.get('habilidades_especiales', 'Sin habilidades'),
                personaje.get('objeto_personal', 'Sin posesiones'),
                personaje.get('imagen', 'Sin imagen')
            ))
            personajes_insertados += 1
            print(f"[{i}] Insertado: {personaje.get('nombre', 'Sin nombre')}")
        except sqlite3.IntegrityError as e:
            personajes_con_error += 1
            print(f"[{i}] Error de integridad con {personaje.get('nombre', 'Sin nombre')}: {e}")
        except Exception as e:
            personajes_con_error += 1
            print(f"[{i}] Error inesperado con {personaje.get('nombre', 'Sin nombre')}: {e}")
    
    # Confirmar los cambios
    conn.commit()
    
    # Mostrar resumen
    total_registros = cursor.execute('SELECT COUNT(*) FROM personajes').fetchone()[0]
    
    print(f"\n{'='*60}")
    print(f" RESUMEN:")
    print(f"{'='*60}")
    print(f"Personajes insertados correctamente: {personajes_insertados}")
    if personajes_con_error > 0:
        print(f"Personajes con errores: {personajes_con_error}")
    print(f"Total de registros en la base de datos: {total_registros}")
    print(f"Base de datos: {db_path}")
    print(f"{'='*60}")
    
    # Cerrar la conexión
    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Insertar personajes desde un archivo JSON a la base de datos SQLite'
    )
    parser.add_argument(
        'archivo_json',
        nargs='?',
        default='./data/personajes.json',
        help='Ruta al archivo JSON con los personajes (por defecto: ./data/personajes.json)'
    )
    parser.add_argument(
        '--db',
        default='./data/overlord.db',
        help='Ruta a la base de datos SQLite (por defecto: ./data/overlord.db)'
    )
    parser.add_argument(
        '--limpiar',
        action='store_true',
        help='Eliminar todos los registros existentes antes de insertar'
    )
    
    args = parser.parse_args()
    
    print(" Insertando personajes de Overlord en la base de datos...\n")
    
    if args.limpiar:
        confirmacion = input("¿Estás seguro de que quieres eliminar todos los registros existentes? (s/N): ")
        if confirmacion.lower() != 's':
            print("Operación cancelada.")
            return
    
    insertar_personajes_desde_json(args.archivo_json, args.db, args.limpiar)
    print("\n ¡Proceso completado!")


if __name__ == "__main__":
    main()