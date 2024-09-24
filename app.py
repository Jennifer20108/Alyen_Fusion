import os
import shutil
import subprocess
import sys
import importlib.util
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for,flash
import sqlite3
from flask import Flask, session 
from flask_session import Session
import secrets
from functools import wraps
import jinja2
import json
import json
from werkzeug.utils import secure_filename

# from CRUD_USER import crear_usuario, leer_usuarios, editar_usuario, borrar_usuario  # Importa las funciones


# Crear una instancia de la aplicación Flask
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuración de Flask-Session
app.config['SECRET_KEY'] = secrets.token_hex(24)   # Reemplaza con una clave secreta segura y única
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Ruta de la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database', 'PRDATA.db')

# Ruta para renderizar la página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Función auxiliar para guardar archivos
def save_file(file, upload_folder):
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)
    return file_path

# Función auxiliar para ejecutar scripts
def run_script(script_name, args=[]):
    result = subprocess.run(['python', script_name] + args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error al ejecutar el script: {result.stderr}")
    return result

# Función auxiliar para mover y eliminar archivos
def move_and_cleanup_files(src, dest):
    try:
        shutil.move(src, dest)
    except FileNotFoundError:
        print(f"El archivo '{src}' no se encontró.")
    except shutil.Error as e:
        print(f"Ocurrió un error al mover el archivo: {e}")
    try:
        os.remove(src)
    except FileNotFoundError:
        print(f"El archivo '{src}' no se encontró para eliminar.")
    except OSError as e:
        print(f"Ocurrió un error al eliminar el archivo: {e}")

# Ruta para ejecutar el script Python NETOS_JS.py
@app.route('/run-python-script', methods=['POST'])
def run_python_script():
    try:
        uploaded_files = request.files.getlist('files[]')  # Obtener la lista de archivos subidos
        print(uploaded_files)
        output_files = []
        for uploaded_file in uploaded_files:
            file_path = save_file(uploaded_file, 'uploads')  # Guardar cada archivo

            # Ejecutar tu script principal para cada archivo
            result = subprocess.run(['python', 'python/NETOS_JS.py', file_path],capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Error al ejecutar el script para {file_path}: {result.stderr}")
            output_file_path = file_path.replace('.xlsx', '.txt') 

            if os.path.isfile(output_file_path):
                output_files.append(os.path.basename(output_file_path))  # Agregar el nombre del archivo de salida a la lista
       
        if output_files:
            return jsonify({'message': 'Scripts ejecutados correctamente.', 'filePaths': output_files})
        else:
            return jsonify({'message': 'No se generaron archivos de salida debido a errores.'}), 500

    except Exception as e:
        return jsonify({'message': 'Error al ejecutar los scripts.', 'error': str(e)}), 500
        
# Ruta para procesar archivos con easycode_resumen
# Ruta para procesar archivos con easycode_resumen
@app.route('/process-easycode-resumen', methods=['POST'])
def process_easycode_resumen():
    try:
        uploaded_files = request.files.getlist('files[]') 
        output_files = []
        for uploaded_file in uploaded_files:
            file_path = save_file(uploaded_file, 'uploads')
            remove_net = request.form.get('remove_net') == 'true'
            format_headers = request.form.get('format_headers') == 'true'
            new_header = request.form.get('new_header', 'InterviewID')

            # Cargar el módulo easycode_resumen dinámicamente
            easycode_resumen_spec = importlib.util.spec_from_file_location("easycode_resumen", os.path.join('python', 'easycode_resumen.py'))
            easycode_resumen = importlib.util.module_from_spec(easycode_resumen_spec)
            sys.modules["easycode_resumen"] = easycode_resumen
            easycode_resumen_spec.loader.exec_module(easycode_resumen)

            output_file, sheets_failed = easycode_resumen.separate_sheets(file_path, remove_net)
            if not output_file:
                return jsonify({'message': 'Error al separar las hojas.', 'sheets_failed': sheets_failed}), 500

            sheets_failed_formatting = easycode_resumen.apply_formatting(output_file)
            if sheets_failed_formatting:
                return jsonify({'message': 'Error al aplicar el formato a las hojas.', 'sheets_failed_formatting': sheets_failed_formatting}), 500

            easycode_resumen.run_summary_script(output_file, new_header)
            output_files.append(os.path.basename(output_file)) 
        if output_files:
            return jsonify({'message': 'Archivos procesados con éxito.', 'filePaths': output_files})
        else:
            return jsonify({'message': 'No se generaron archivos de salida debido a errores.'}), 500   
    except Exception as e:
        return jsonify({'message': 'Error al procesar los archivos.', 'error': str(e)}), 500



# Ruta para ejecutar el script Python runBat.py
@app.route('/run-bat-form', methods=['POST'])
def process_runBat():
    try:
        file_path = save_file(request.files['file'], 'uploads')
        absolute_output_file = os.path.abspath('uploads/')
        run_script('python/runBat.py', [absolute_output_file])

        move_and_cleanup_files('Runit.bat', 'uploads/')
        
        return jsonify({'message': 'Archivo procesado con éxito.', 'filePath': os.path.basename(os.path.abspath('uploads/Runit.bat'))})
    except Exception as e:
        return jsonify({'message': 'Error al procesar el archivo.', 'error': str(e)}), 500

# Ruta para ejecutar el script Python SAV_EXCEL.py
@app.route('/mapeo-spss', methods=['POST'])
def process_mapeo_spss():
    try:
        uploaded_files = request.files.getlist('files[]')
        output_files = []
        
        for uploaded_file in uploaded_files:
            file_path = save_file(uploaded_file, 'uploads')
            absolute_output_file = os.path.abspath(file_path)
            run_script('python/SAV_EXCEL.py', [absolute_output_file])

            output_file = file_path.replace(".sav", ".xlsx")
            # move_and_cleanup_files(output_file, 'uploads/')

            output_files.append(os.path.basename(os.path.abspath(f'uploads/{output_file}')))

        if output_files:
            return jsonify({'message': 'Archivos procesados con éxito.', 'filePaths': output_files})
        else:
            return jsonify({'message': 'No se generaron archivos de salida debido a errores.'}), 500

    except Exception as e:
        return jsonify({'message': 'Error al procesar los archivos.', 'error': str(e)}), 500


# Ruta para ejecutar el script Python formateo.py
@app.route('/formateo-artifac', methods=['POST'])
def process_formateo_artifac():
    # try:
    #     file_path = save_file(request.files['file'], 'uploads')
    #     run_script('python/formateo.py', ['uploads/'])

    #     move_and_cleanup_files('archivos_xls.zip', 'uploads/')

    #     return jsonify({'message': 'Archivo procesado con éxito.', 'filePath': os.path.basename(os.path.abspath('uploads/archivos_xls.zip'))})
    # except Exception as e:
    #     return jsonify({'message': 'Error al procesar el archivo.', 'error': str(e)}), 500
    try:
        uploaded_files = request.files.getlist('files[]')

        for uploaded_file in uploaded_files:
            save_file(uploaded_file, 'uploads')  # Guardar cada archivo en 'uploads/'

        # Ejecutar el script formateo.py una vez para procesar todos los archivos en 'uploads/'
        run_script('python/formateo.py', ['uploads/'])

        move_and_cleanup_files('archivos_xls.zip', 'uploads/')

        return jsonify({'message': 'Archivos procesados con éxito.', 'filePath': 'archivos_xls.zip'})

    except Exception as e:
        return jsonify({'message': 'Error al procesar los archivos.', 'error': str(e)}), 500
# Ruta para ejecutar el script Python validacion.py
@app.route('/val-bdd-ldc', methods=['POST'])
def process_val_bdd_ldc():
    try:
        uploaded_files = request.files.getlist('files[]')

        output_files = []
        for i, uploaded_file in enumerate(uploaded_files):  # Use enumerate for index and file
            file_path = save_file(uploaded_file, 'uploads')
            absolute_output_file = os.path.abspath(file_path)

            file_name_base = os.path.splitext(os.path.basename(file_path))[0]

            run_script('python/validacion.py', [absolute_output_file])

            output_file = f"{file_name_base}_V{i+1}.xlsx"  # Start index at 1 for user-friendliness

            # Move and cleanup within the 'uploads' directory
            move_and_cleanup_files(f"{file_name_base}.xlsx", f'uploads/{output_file}')

            if os.path.isfile(f'uploads/{output_file}'):  # Check if file exists in 'uploads'
                output_files.append(output_file)  # Append just the filename

                print(output_file, "fgaaaaaaaaaaaa")  # Debugging output

        if output_files:
            return jsonify({'message': 'Archivos procesados con éxito.', 'filePaths': output_files})
        else:
            return jsonify({'message': 'No se generaron archivos de salida debido a errores.'}), 500
    except Exception as e:
        return jsonify({'message': 'Error al procesar los archivos.', 'error': str(e)}), 500
    
# Ruta para servir los archivos generados
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    uploads = 'uploads'
    file_path = os.path.join(uploads, filename)
    if not os.path.isfile(file_path):
        return jsonify({'message': 'Archivo no encontrado.'}), 404
    return send_from_directory(directory=uploads, path=filename, as_attachment=True)

@app.route('/delete-files', methods=['POST'])
def delete_files():
    try:
        uploads_folder = 'uploads'
        if os.path.exists(uploads_folder):
            shutil.rmtree(uploads_folder)  # Elimina todo el contenido de la carpeta 'uploads'
        os.makedirs(uploads_folder)  # Vuelve a crear la carpeta 'uploads' vacía

        return jsonify({'message': 'Contenido de la carpeta "uploads" eliminado correctamente.'})

    except Exception as e:
        return jsonify({'message': 'Error al eliminar el contenido de la carpeta "uploads".', 'error': str(e)}), 500

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs): 
        if 'user_id' not in session:
            return redirect(url_for('login')) 
        return f(*args, **kwargs)
    return decorated_function

# Otras rutas
@app.route('/panel')
@login_required
def panel():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirigir si no está logueado

    # Conectar a la base de datos y obtener los datos del usuario
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, apellido, correo, celular, direccion, imagen_perfil, tipos_user FROM usuarios WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        # Extraer datos
        nombre, apellido, correo, celular, direccion, imagen_perfil, tipos_user = usuario
        
        # Asignar una imagen predeterminada si es None o vacío
        if not imagen_perfil:
            imagen_perfil = 'default_avatar.png'
        
        return render_template('panel.html', 
                               nombre=nombre, 
                               apellido=apellido, 
                               correo=correo, 
                               celular=celular, 
                               direccion=direccion, 
                               imagen_perfil=imagen_perfil,
                               tipos_user=tipos_user)
    else:
        return redirect(url_for('login'))  # Redirigir si el usuario no se encuentra

@app.route('/panel_admin')
@login_required
def panel_admin():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirigir si no está logueado

    # Conectar a la base de datos y obtener los datos del usuario
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, apellido, correo, celular, direccion, imagen_perfil, tipos_user FROM usuarios WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()

# Obtener todos los usuarios para la vista
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    if usuario:
        nombre, apellido, correo, celular, direccion, imagen_perfil, tipos_user = usuario
        if tipos_user != "Administrador":
            conn.close()
            return redirect(url_for('login'))  # Redirigir si no es Administrador
        
        if not imagen_perfil:
            imagen_perfil = 'default_avatar.png'
        
        return render_template('panel_admin.html', 
                               nombre=nombre, 
                               apellido=apellido, 
                               correo=correo, 
                               celular=celular, 
                               direccion=direccion, 
                               imagen_perfil=imagen_perfil,
                               tipos_user=tipos_user,
                               usuarios=usuarios)  # Pasa la lista de usuarios
    else:
        return redirect(url_for('login'))

@app.route('/nosotros')
def Nosotros():
    return render_template('nosotros.html')



@app.route('/login')
def login():
    return render_template('login.html')

def escapejs_filter(value):
    return jinja2.escape(value).replace('"', '\\"').replace("'", "\\'")

app.jinja_env.filters['escapejs'] = escapejs_filter

@app.route('/control', methods=['GET', 'POST'])

def control():
    if request.method == 'GET':
        opc = request.args.get('opc')
        if opc == '0':
            correo = request.args.get('correo')
            contrasena = request.args.get('contrasena')
            try:
                # Conectar a la base de datos
                conn = sqlite3.connect(db_path) 
                cursor = conn.cursor()

                # Consulta para verificar si el correo existe
                cursor.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,))
                usuario = cursor.fetchone()

                conn.close()

                if usuario:
                    # Verificar la contraseña
                    if usuario[4] == contrasena:  # Asumiendo que la contraseña está en la columna 4
                        session['user_id'] = usuario[0]  # Almacena el ID del usuario en la sesión
                        return redirect(url_for('panel'))
                    else:
                        # Contraseña incorrecta
                        password_error_message = json.dumps('La contraseña es incorrecta')
                        return render_template('login.html', password_error=password_error_message)
                else:
                    # Usuario no encontrado
                    error_message = json.dumps('El correo no está registrado')
                    return render_template('login.html', error=error_message)

            except sqlite3.Error as e:
                error_message = json.dumps(f"Error al verificar credenciales: {e}")
                return render_template('login.html', error=error_message)     

    elif request.method == 'POST':
        opc = request.form.get('opc')
        if opc == '7':  # Asumimos que '7' es la opción de registro
            try:
                # Obtener datos del formulario
                nombre = request.form['nombre']
                apellido = request.form['apellido']
                correo = request.form['correo']
                contrasena = request.form['contrasena']
                celular = request.form['celular']
                direccion = request.form['direccion']
                imagen = request.files['imagen']
                tipos_user = request.form['tipos_user']
                estado_user ='Pendiente'
                # Conectar a la base de datos
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Verificar si el correo ya existe
                cursor.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,))
                usuario_existente = cursor.fetchone()

                if usuario_existente:
                    conn.close()
                    return render_template('login.html', error=f"El correo electrónico '{correo}' ya está registrado. Por favor, usa otro correo.")

                # Validar la imagen
                if imagen:
                    # Define la carpeta donde se guardarán las imágenes
                    upload_folder = os.path.join(basedir, 'static', 'images', 'perfil')
                    os.makedirs(upload_folder, exist_ok=True)

                    # Guarda la imagen
                    imagen_filename = secure_filename(imagen.filename)
                    imagen_path = os.path.join(upload_folder, imagen_filename)
                    imagen.save(imagen_path)

                    # Insertar datos en la base de datos, incluyendo la ruta de la imagen
                    cursor.execute("INSERT INTO usuarios (nombre, apellido, correo, contrasena, celular, direccion, imagen_perfil, tipos_user, estado_user) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                        (nombre, apellido, correo, contrasena, celular, direccion, imagen_filename, tipos_user, estado_user))

                    conn.commit()
                    conn.close()

                    return render_template('login.html', success="Registro exitoso. Puedes iniciar sesión ahora.")
                else:
                    flash('Por favor selecciona una imagen.')

            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    return render_template('login.html', error=f"El correo electrónico '{correo}' ya está registrado. Por favor, usa otro correo.")
                else:
                    return render_template('login.html', error=f"Error al registrar usuario: {e}")
            except sqlite3.Error as e:
                return render_template('login.html', error=f"Error al registrar usuario: {e}")


@app.route('/success')
def success():
    return "Registro exitoso"




@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))  # O a la página que desees


# NUEVO JS 21/09/2024

@app.route('/leer_usuarios', methods=['GET', 'POST'])
@login_required
def leer_usuarios():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # Conectar a la base de datos y verificar tipo de usuario
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT tipos_user FROM usuarios WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()

    if usuario and usuario[0] == "Administrador":
        if request.method == 'POST':
            busqueda = request.form.get('busqueda', '')
            cursor.execute("SELECT * FROM usuarios WHERE nombre LIKE ? OR apellido LIKE ?", 
                           ('%' + busqueda + '%', '%' + busqueda + '%'))
        else:
            cursor.execute("SELECT * FROM usuarios")
        
        usuarios = cursor.fetchall()
        conn.close()
        return render_template('panel_admin.html', usuarios=usuarios)
    
    conn.close()
    return redirect(url_for('login'))  # Redirigir si no es Administrador

@app.route('/nuevo_usuario', methods=['GET', 'POST'])
@login_required
def nuevo_usuario():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT tipos_user FROM usuarios WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()

    if usuario and usuario[0] == "Administrador":
        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            correo = request.form['correo']
            contrasena = request.form['contrasena']
            celular = request.form['celular']
            direccion = request.form['direccion']
            imagen_perfil = request.files.get('imagen_perfil')
            tipos_user = request.form['tipos_user']
            estado_user = request.form['estado_user']

            imagen_perfil_filename = imagen_perfil.filename if imagen_perfil else None
            if imagen_perfil:
                imagen_perfil.save(os.path.join('static/images/perfil', imagen_perfil_filename))

            try:
                cursor.execute('INSERT INTO usuarios (nombre, apellido, correo, contrasena, celular, direccion, imagen_perfil, tipos_user, estado_user) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                               (nombre, apellido, correo, contrasena, celular, direccion, imagen_perfil_filename, tipos_user, estado_user))
                conn.commit()

                return jsonify(success=True, message="Usuario creado exitosamente.")
            except Exception as e:
                return jsonify(success=False, message=f'Error: {str(e)}'), 500
            finally:
                conn.close()

        return render_template('nuevo_usuario.html')

    return redirect(url_for('login'))


# @app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
# @login_required
# def editar_usuario(id):
#     user_id = session.get('user_id')
#     if not user_id:
#         return jsonify(success=False, message='No estás autenticado.'), 403

#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute("SELECT tipos_user FROM usuarios WHERE id = ?", (user_id,))
#     usuario = cursor.fetchone()

#     if usuario and usuario[0] == "Administrador":
#         cursor.execute('SELECT * FROM usuarios WHERE id = ?', (id,))
#         usuario_data = cursor.fetchone()

#         if request.method == 'POST':
#             try:
#                 nombre = request.form['nombre']
#                 apellido = request.form['apellido']
#                 correo = request.form['correo']
#                 contrasena = request.form['contrasena']
#                 celular = request.form['celular']
#                 direccion = request.form['direccion']
#                 imagen_perfil = request.files.get('imagen_perfil')
#                 tipos_user = request.form['tipos_user']
#                 estado_user = request.form['estado_user']

#                 imagen_perfil_filename = imagen_perfil.filename if imagen_perfil else usuario_data[7]
#                 if imagen_perfil:
#                     imagen_perfil.save(os.path.join('static/images/perfil', imagen_perfil_filename))

#                 cursor.execute('UPDATE usuarios SET nombre = ?, apellido = ?, correo = ?, contrasena = ?, celular = ?, direccion = ?, imagen_perfil = ?, tipos_user = ?, estado_user = ? WHERE id = ?',
#                                (nombre, apellido, correo, contrasena, celular, direccion, imagen_perfil_filename, tipos_user, estado_user, id))
#                 conn.commit()

#                 return jsonify(success=True, message="Usuario actualizado exitosamente.")
#             except Exception as e:
#                 return jsonify(success=False, message=f'Error: {str(e)}'), 500

#         return render_template('editar_usuario.html', usuario=usuario_data)

#     return jsonify(success=False, message='No tienes permisos para editar este usuario.'), 403

@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message='No estás autenticado.'), 403

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT tipos_user FROM usuarios WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()

    if usuario and usuario[0] == "Administrador":
        cursor.execute('SELECT * FROM usuarios WHERE id = ?', (id,))
        usuario_data = cursor.fetchone()

        if request.method == 'POST':
            try:
                nombre = request.form['nombre']
                apellido = request.form['apellido']
                correo = request.form['correo']
                contrasena = request.form['contrasena']
                celular = request.form['celular']
                direccion = request.form['direccion']
                imagen_perfil = request.files.get('imagen_perfil')
                tipos_user = request.form['tipos_user']
                estado_user = request.form['estado_user']

                if imagen_perfil:
                    imagen_perfil.save(os.path.join('static/images/perfil', imagen_perfil.filename))
                    imagen_perfil_filename = imagen_perfil.filename
                else:
                    imagen_perfil_filename = usuario_data[7]  # Mantener la imagen anterior

                cursor.execute('UPDATE usuarios SET nombre = ?, apellido = ?, correo = ?, contrasena = ?, celular = ?, direccion = ?, imagen_perfil = ?, tipos_user = ?, estado_user = ? WHERE id = ?',
                               (nombre, apellido, correo, contrasena, celular, direccion, imagen_perfil_filename, tipos_user, estado_user, id))
                conn.commit()

                return jsonify(success=True, message="Usuario actualizado exitosamente.")
            except Exception as e:
                return jsonify(success=False, message=f'Error: {str(e)}'), 500
            finally:
                conn.close()

        return render_template('editar_usuario.html', usuario=usuario_data)

    conn.close()
    return jsonify(success=False, message='No tienes permisos para editar este usuario.'), 403
# @app.after_request
# def add_header(response):
#     response.cache_control.max_age = 0
#     return response

@app.route('/borrar_usuario/<int:id>', methods=['POST'])
@login_required
def borrar_usuario(id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # Conectar a la base de datos y verificar tipo de usuario
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT tipos_user FROM usuarios WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()

    if usuario and usuario[0] == "Administrador":
        try:
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
            conn.commit()
            flash('Usuario eliminado exitosamente.', 'success')
        except Exception as e:
            flash(f'Error al eliminar el usuario: {str(e)}', 'error')
    else:
        flash('No tienes permiso para eliminar usuarios.', 'error')

    conn.close()
    return redirect(url_for('panel_admin'))  # Redirigir al panel de administración


# Punto de entrada para ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)

