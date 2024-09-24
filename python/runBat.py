import os
import sys

def crear_archivo_ejecucion(path):
    files = os.listdir(path)
    files.sort()
    output_file = open("Runit.bat", "w")

    # Get the .mdd file (assuming there's only one)
    JOB = next((archivo for archivo in os.listdir(path) if archivo.endswith(".mdd")), None)

    # Handle the case where no .mdd file is found
    if JOB is None:
        print("Error: No se encontró ningún archivo .mdd en el directorio.")
        return

    output_file.write(f'CLS\n')
    output_file.write(f"\n")
    output_file.write(f'setlocal\n') 
    output_file.write(f'set "JOB={JOB[:-4]}"\n')  # Remove the .mdd extension
    output_file.write(f"\n")

    output_file.write(f'::Ejecutando scripts de proceso\n') 
    output_file.write(f"\n")
    for filename in files:
        if filename.endswith((".dms", ".mrs")):
            new_filename = filename.replace(filename.split('_', 1)[0], "%JOB%", 1)
            command = 'DMSRUN' if filename.endswith(".dms") else 'mrscriptcl'
            output_file.write(f'{command} "{new_filename}" /s\n')

    output_file.write(f"\n")
    output_file.write(f'::Ejecutando scripts de generacion de Tablas\n') 
    output_file.write(f"\n")
    output_file.write(f'cd .. \n') 
    output_file.write(f'cd Proceso\n')  # Removed extra space
    output_file.write(f'start ./ReportsMTD.bat \n')
    output_file.write(f"\n")
    output_file.write(f'::Ejecutando PY de Artifac para la generacion de MTDs\n') 
    output_file.write(f"\n")
    output_file.write(f'python.exe formateo.py\n')
    output_file.write(f'pause\n')
    output_file.close()

def main(path):
    crear_archivo_ejecucion(path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Por favor, proporcione la ruta como argumento.")
    else:
        path = sys.argv[1]
        main(path)