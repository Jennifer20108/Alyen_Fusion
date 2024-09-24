# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 04:11:26 2024

@author: Anthony.Vivian
"""
#importamos las librerias a usar
import pandas as pd
import pyreadstat
import tkinter as tk
from tkinter import filedialog, messagebox
#from tkinter import PhotoImage
import os
import sys

from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os

#evita que el boton se cree multiples veces
boton_creado = False


# def seleccionar_archivo():
#     archivo = filedialog.askopenfilename(
#         title="Selecciona la base SPSS",
#         filetypes=[("Archivos SPSS", "*.sav")]
#     )
#     return archivo

def generar_nombre_archivo(archivo_spss):
    carpeta = os.path.dirname(archivo_spss)
    nombre_archivo_base = os.path.splitext(os.path.basename(archivo_spss))[0]
    archivo_excel = os.path.join(carpeta, f"{nombre_archivo_base}.xlsx")
    
    # Comprueba que el archivo no existe, de hacerlo le agrega la version que corresponde.
    version = 1
    while os.path.exists(archivo_excel):
        archivo_excel = os.path.join(carpeta, f"{nombre_archivo_base}_V{version}.xlsx")
        version += 1
    
    return archivo_excel

    #pasa la base sav a excel
def convertir_spss_a_excel(path):
    # archivo_spss = seleccionar_archivo()
    
    archivo_spss = path
    
    if not archivo_spss:
        return
    
    archivo_excel = generar_nombre_archivo(archivo_spss)
    
    try:
        df, meta = pyreadstat.read_sav(archivo_spss)
        
        # Crear un DataFrame con códigos en lugar de etiquetas
        df_codigos = df.copy()
        
        # Reemplazar etiquetas por códigos en el DataFrame de códigos
        for column in df_codigos.columns:
            if column in meta.variable_value_labels:
                df_codigos[column] = df_codigos[column].map(meta.variable_value_labels[column])
        
        # Guardar ambos DataFrames en diferentes hojas de un archivo Excel
        with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Codigo', index=False)  # Guardar con Codigos
            df_codigos.to_excel(writer, sheet_name='Etiqueta', index=False)  # Guardar con códigos
        
        # messagebox.showinfo("Éxito", f"Archivo guardado correctamente en {archivo_excel}")
        
        # Cerrar la ventana de tkinter una vez que se confirme la exportación
        # root.destroy()
    except Exception as e:
        print(f"Error: {str(e)}")



def main(path):
    convertir_spss_a_excel(path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Por favor, proporcione la ruta como argumento.")
    else:
        path = sys.argv[1]
        main(path)
       
# def crear_boton_convertir():
#     global boton_creado
    
#     if boton_creado:
#         messagebox.showwarning("Advertencia!!", "El botón ya está creado.")
#     else:        
#         # Crear un botón cuadrado para iniciar la conversión
#         btn_convertir = tk.Button(root, text="Seleccionar la base SPSS", command=convertir_spss_a_excel, width=20, height=4)
#         btn_convertir.pack(expand=True)
#         boton_creado = True        

# # Configurar la interfaz gráfica
# root = tk.Tk()
# root.title("Convertir SPSS a Excel")

# # Tamaño de la ventana(definimos)
# window_width = 200
# window_height = 300

# # Obtener el tamaño de la pantalla
# screen_width = root.winfo_screenwidth()
# screen_height = root.winfo_screenheight()

# # Calcular la posición para centrar la ventana en la pantalla
# position_top = int(screen_height/2 - window_height/2)
# position_right = int(screen_width/2 - window_width/2)

# # Establecer el tamaño de la pantalla de la laptop
# root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")


# # es para añadir imagen, pero no se dio
# # # Agregar imagen a la cabecera (opcional)
# # imagen = PhotoImage(file="C:/Users/Anthony.Vivian/OneDrive - Ipsos/Desktop/proyecto/APP_FLASK/python/Logo_ipsos.png")  # Reemplaza con la ruta de tu imagen
# # label_imagen = tk.Label(root, image=imagen)
# # label_imagen.pack(pady=10)

# # Crear un botón para iniciar la conversión
# # btn_convertir = tk.Button(root, text="Seleccionar la base SPSS", command=convertir_spss_a_excel)
# # btn_convertir.pack(pady=35, expand=True)


# btn_convertir = tk.Button(root, text="Seleccionar la base SPSS", command=convertir_spss_a_excel, width=20, height=4)
# btn_convertir.pack(expand=True)

# # Ajusta según el tamaño de la ventana deseada
# root.geometry("250x100")  


# # arranca la aplicación
# root.mainloop()
