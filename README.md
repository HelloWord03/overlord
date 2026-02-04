# Overlord -- Gestor de Personajes

Aplicación web desarrollada con Flask para la gestión de personajes del
universo *Overlord*. Permite crear, visualizar, editar y eliminar
personajes, así como asociar imágenes almacenadas en el servidor 
y descargar un csv con todos los personajes o solo el seleccionado .

El proyecto incluye además un script en Python para importar personajes
desde un archivo JSON a la base de datos SQLite utilizada por la
aplicación.

## Tecnologías utilizadas

-   Python 3
-   Flask
-   SQLAlchemy
-   HTML / Jinja2
-   CSS
-   JSON
-   argparse

## Estructura del proyecto

proyecto/ 
│── app.py 
│── insertar_personajes.py 
│── README.md 
│ 
├──data/ 
│   ├── overlord.db 
│   └── personajes.json 
│ 
├── static/ 
│   ├──imagenes/ 
│   │    └── nazarick.jpg 
│   └──css/ 
│       └── estilo.css 
│   
└── templates/ 
    ├── index.html 
    ├── base.html 
    ├── crear.html 
    ├── editar.html 
    └── ver.html

## Requisitos

-   Python 3.8 o superior

Instalar Flask si no está disponible:

pip install flask

## Ejecución

python app.py

http://127.0.0.1:5000

## Importación desde JSON

python insertar_personajes.py

## Autor

Proyecto realizado con fines educativos.
Ariannet Alvarez, Mikel Martin
