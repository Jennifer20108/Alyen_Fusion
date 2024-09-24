import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('database/PRDATA.db')

# Crear un cursor para ejecutar comandos SQL
cursor = conn.cursor()

# Lista de nuevas columnas a agregar
nuevas_columnas = [
    ('imagen_perfil', 'TEXT'),
    ('Tipos_User', 'TEXT'),
    ('estado_User', 'TEXT')
]

# Agregar nuevos campos a la tabla 'usuarios'
for columna, tipo in nuevas_columnas:
    try:
        cursor.execute(f'ALTER TABLE usuarios ADD COLUMN {columna} {tipo}')
        print(f"Campo '{columna}' agregado exitosamente.")
    except sqlite3.OperationalError as e:
        print(f"Error al agregar el campo '{columna}':", e)

# Confirmar los cambios en la base de datos
conn.commit()

# Cerrar la conexión
conn.close()
