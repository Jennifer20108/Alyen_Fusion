# crud.py
import sqlite3

def crear_usuario(nombre, apellido, correo, contrasena, celular, direccion, imagen_perfil, tipos_user, estado_user):
    with sqlite3.connect('database/PRDATA.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nombre, apellido, correo, contrasena, celular, direccion, imagen_perfil, Tipos_User, estado_User)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, apellido, correo, contrasena, celular, direccion, imagen_perfil, tipos_user, estado_user))
        conn.commit()

def leer_usuarios():
    with sqlite3.connect('database/PRDATA.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios')
        return cursor.fetchall()

def actualizar_usuario(id_usuario, imagen_perfil, tipos_user, estado_user):
    with sqlite3.connect('database/PRDATA.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE usuarios SET imagen_perfil = ?, Tipos_User = ?, estado_User = ? WHERE id = ?
        ''', (imagen_perfil, tipos_user, estado_user, id_usuario))
        conn.commit()

def borrar_usuario(id_usuario):
    with sqlite3.connect('database/PRDATA.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM usuarios WHERE id = ?', (id_usuario,))
        conn.commit()
