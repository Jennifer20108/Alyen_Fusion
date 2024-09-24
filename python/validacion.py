import pandas as pd
import math
import sys
import os

def encontrar_enc_diferentes(ruta_archivo):
  # Leer el archivo Excel en un objeto ExcelFile
  excel_data = pd.ExcelFile(ruta_archivo)

  # Obtener la lista de nombres de las hojas
  nombres_hojas = excel_data.sheet_names

  # Cargar la primera hoja (LDC) en un DataFrame
  df_ldc = pd.read_excel(excel_data, sheet_name=0)
  # Crear una lista para almacenar los resultados de todas las hojas
  resultados_hojas =[]
  # Iterar sobre las hojas del archivo Excel (excluyendo la primera hoja)
  for i in range(1, len(nombres_hojas)):
    # Cargar la hoja actual en un DataFrame
    df = pd.read_excel(excel_data, sheet_name=i)

    # Crear una lista vacía para almacenar los valores de "ENC" que cumplen la condición en la hoja actual
    enc_encontrados = []
    cod_encontrados =[]
    # Iterar sobre cada fila del DataFrame de la hoja actual
    for index, row in df.iterrows():
      # Iterar sobre las columnas "Cod_#"
      for col in df.columns:
        if col.startswith("Cod_"):
            valor_cod = row[col]  # Obtener el valor en la columna "Cod_#"
            # Buscar el "Code" correspondiente en la primera hoja (LDC), considerando la variable actual
            fila_ldc = df_ldc[(df_ldc["Code"] == valor_cod) & (df_ldc["Variable"] == row["Variable"])]
            # Verificar si se encontró el "Code" en la primera hoja (LDC) para la variable actual
            if fila_ldc.empty and pd.notna(valor_cod):
                # Agregar el valor de "ENC" a la lista de resultados de la hoja actual
                enc_encontrados.append(row["ENC"])
                cod_encontrados.append(valor_cod)
              # Pasar a la siguiente fila si ya se encontró un valor que cumple la condición
              #  break
    resultados_hojas.append({
        "nombre_hoja": nombres_hojas[i],"enc_encontrados": enc_encontrados,"cod_encontrados": cod_encontrados})
        
   # Devolver la lista de resultados de todas las hojas
  return resultados_hojas

def main(path):
    ruta_archivo = path  # Reemplaza con la ruta de tu archivo
    nombre_archivo = os.path.basename(ruta_archivo)
    resultados = encontrar_enc_diferentes(ruta_archivo)
    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_excel(f"{nombre_archivo}", index=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Por favor, proporcione la ruta como argumento.")
    else:
        path = sys.argv[1]
        main(path)
