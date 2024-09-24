import os
import shutil
import time
import concurrent.futures
import re
import asyncio

import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np
import os
import sys

import tkinter as tk
from tkinter import filedialog
import zipfile

def rellenar_espacios_con_interrogante(texto):
    texto_modificado = texto.replace(' ', '?')
    return texto_modificado

async def ejecutar_comando(archivo_mtd, archivos_mtd, RUTA_ARTIFACTO, PLANTILLA_CDS, PLANTILLA_SDS, ORIGEN, DESTINO_CDS, DESTINO_SDS):
    indice = archivos_mtd.index(archivo_mtd)
    
    archivo_mtd=path+archivo_mtd
    #parche de emergencia luego reviasarlo-....
    print(archivo_mtd)
    PRIMERO_CDS = "\"" + RUTA_ARTIFACTO + "\" -y,-xlsx,-"+ PLANTILLA_CDS +"?-?" + str(indice+2) + ".xml,"
    PRIMERO_SDS = "\"" + RUTA_ARTIFACTO + "\" -y,-xlsx,-"+ PLANTILLA_SDS +"?-?" + str(indice+2) + ".xml,"

    ORIGEN_MTD = ORIGEN.replace("mtd", archivo_mtd)
    DESTINO_XLSX_CDS = DESTINO_CDS.replace("mtd", archivo_mtd.replace(".mtd", ".xlsx"))
    DESTINO_XLSX_SDS = (DESTINO_SDS.replace("mtd", archivo_mtd.replace(".mtd", ".xlsx"))).replace("CDS", "SDS")

    COMANDO_CDS = PRIMERO_CDS + ORIGEN_MTD + DESTINO_XLSX_CDS
    COMANDO_SDS = PRIMERO_SDS + ORIGEN_MTD + DESTINO_XLSX_SDS

    print(COMANDO_CDS)
    print(COMANDO_SDS)

    proc_cds = await asyncio.create_subprocess_shell(COMANDO_CDS)
    proc_sds = await asyncio.create_subprocess_shell(COMANDO_SDS)

    await proc_cds.communicate()
    await proc_sds.communicate()

    await asyncio.sleep(30)

async def formatear_archivos_parallel(path):
    USUARIO=os.getlogin()
    RUTA_ARTIFACTO = fr"C:\Users\{USUARIO}\OneDrive - Ipsos\Desktop\Artifact.appref-ms"
    RUTA_PRESETS = fr"C:\Users\{USUARIO}\AppData\Roaming\Ipsos\ARTIFACT\Presets\CRTs"
    ORIGEN = os.getcwd() + "\\mtd" + ","
    ORIGEN = ORIGEN.replace(" ", "?")
    DESTINO_CDS = ORIGEN.rstrip(",")
    DESTINO_SDS = DESTINO_CDS
    PLANTILLA_CDS="Plantilla Artifact (CDSig)"
    PLANTILLA_SDS="Plantilla Artifact (SDSig)"

    archivos_mtd = [nombre_archivo for nombre_archivo in os.listdir(path) if nombre_archivo.endswith(".mtd")]
    for i, archivo_mtd in enumerate(archivos_mtd):
        nombre_archivo_cds = f"{PLANTILLA_CDS} - {i+2}.xml"
        nombre_archivo_sds = f"{PLANTILLA_SDS} - {i+2}.xml"

        ruta_archivo_destino_cds = os.path.join(RUTA_PRESETS, nombre_archivo_cds)
        ruta_archivo_destino_sds = os.path.join(RUTA_PRESETS, nombre_archivo_sds)

        if not os.path.exists(ruta_archivo_destino_cds):
            shutil.copy2(os.path.join(RUTA_PRESETS, f"{PLANTILLA_CDS} - 1.xml"), ruta_archivo_destino_cds)

        if not os.path.exists(ruta_archivo_destino_sds):
            shutil.copy2(os.path.join(RUTA_PRESETS, f"{PLANTILLA_SDS} - 1.xml"), ruta_archivo_destino_sds)

    PLANTILLA_CDS = rellenar_espacios_con_interrogante(PLANTILLA_CDS)
    PLANTILLA_SDS = rellenar_espacios_con_interrogante(PLANTILLA_SDS)

    # Usamos asyncio.gather para ejecutar las tareas de forma concurrente
    tasks = [ejecutar_comando(archivo_mtd, archivos_mtd, RUTA_ARTIFACTO, PLANTILLA_CDS, PLANTILLA_SDS, ORIGEN, DESTINO_CDS, DESTINO_SDS) for archivo_mtd in archivos_mtd]
    await asyncio.gather(*tasks)

    def zip_xls_files(directory_path, zip_filename):
        """
        Esta función comprime todos los archivos XLS en un directorio específico en un archivo ZIP.

        Args:
            directory_path (str): La ruta al directorio que contiene los archivos XLS.
            zip_filename (str): El nombre del archivo ZIP que se creará.
        """

        with zipfile.ZipFile(zip_filename, 'w') as zip_file:
            for filename in os.listdir(directory_path):
                if filename.endswith('.xls') or filename.endswith('.xlsx'):
                    filepath = os.path.join(directory_path, filename)
                    zip_file.write(filepath, filename)

    directory_to_zip = path  # Reemplaza con la ruta real
    output_zip_file = 'archivos_xls.zip'

    zip_xls_files(directory_to_zip, output_zip_file)
    print(f"Archivos XLS comprimidos en {output_zip_file}")

async def main(path):
    await formatear_archivos_parallel(path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Por favor, proporcione la ruta como argumento.")
    else:
        path = sys.argv[1]
        asyncio.run(main(path))