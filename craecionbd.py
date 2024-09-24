import sqlite3

# Conectar a la base de datos (si no existe, se creará)
conn = sqlite3.connect('PRDATA.db')  # Reemplaza 'tu_base_de_datos.db' con el nombre deseado

# Crear un cursor para ejecutar comandos SQL
cursor = conn.cursor()

# Definir la estructura de la tabla 'usuarios'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        correo TEXT NOT NULL UNIQUE,
        contrasena TEXT NOT NULL,
        celular TEXT NOT NULL,
        direccion TEXT NOT NULL
    )
''')

# Confirmar los cambios en la base de datos
conn.commit()

# Cerrar la conexión
conn.close()