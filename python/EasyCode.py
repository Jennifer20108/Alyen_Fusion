import pandas as pd
import subprocess
import re
import os

def clean_sheet_name(sheet_name):
    """Limpia y ajusta el nombre de la hoja para cumplir con los requisitos de Excel."""
    sheet_name = sheet_name.replace('[', '.').replace(']', '').replace('{', '.').replace('}', '')
    sheet_name = re.sub(r'\.{2,}', '.', sheet_name)
    return sheet_name[:31]

def remove_net_columns(df):
    # """Elimina las columnas que comienzan con 'NET_'."""
    net_columns = [col for col in df.columns if col.startswith('NET_')]
    df = df.drop(columns=net_columns, errors='ignore')
    return df

def format_headers(df):
    # """Renombra las columnas después de 'Verbatim' con COD_1, COD_2, etc."""
    if 'Verbatim' in df.columns:
        verbatim_index = df.columns.get_loc('Verbatim')
        new_column_names = df.columns[:verbatim_index+1].tolist()
        for i, col in enumerate(df.columns[verbatim_index+1:], start=1):
            new_column_names.append(f'COD_{i}')
        df.columns = new_column_names
    return df

def process_verbatim_code(sheet_data, writer):
    # """Procesa la hoja 'Verbatim Code' y separa en hojas basadas en 'Question'."""
    if 'Question' in sheet_data.columns:
        questions = sheet_data['Question'].unique()
        for question in questions:
            df_filtered = sheet_data[sheet_data['Question'] == question]
            filtered_name = clean_sheet_name(str(question))
            if not df_filtered.empty:
                df_filtered.to_excel(writer, sheet_name=filtered_name, index=False)
    return writer

def separate_sheets(file_path, remove_net):
    """Lee el archivo y separa las hojas según la columna 'Question'."""
    output_file = os.path.join('uploads', '4_Codificacion_Easy_Code.xlsx')
    sheets_failed = []

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df = pd.read_excel(file_path, sheet_name=None)  # Lee todas las hojas
        
        for sheet_name, data in df.items():
            if data.empty:
                continue

            if remove_net:
                data = remove_net_columns(data)
            
            if sheet_name == 'Verbatim Code':
                writer = process_verbatim_code(data, writer)
            else:
                clean_name = clean_sheet_name(sheet_name)
                try:
                    data.to_excel(writer, sheet_name=clean_name, index=False)
                except Exception as e:
                    sheets_failed.append(sheet_name)
    
    if sheets_failed:
        return None, sheets_failed

    return output_file, None

def apply_formatting(output_file):
    """Aplica el formateo de encabezados a las hojas que contienen la columna 'Verbatim'."""
    temp_file = os.path.join('uploads', 'temp_formatting.xlsx')
    sheets_failed = []

    with pd.ExcelFile(output_file) as xls:
        with pd.ExcelWriter(temp_file, engine='openpyxl') as writer:
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                if 'Verbatim' in df.columns:
                    df = format_headers(df)
                try:
                    df.to_excel(writer, sheet_name=clean_sheet_name(sheet_name), index=False)
                except Exception as e:
                    sheets_failed.append(sheet_name)

    if not sheets_failed:
        os.replace(temp_file, output_file)
    else:
        return sheets_failed

def run_summary_script(output_file):
    """Ejecuta resumen.py con el archivo de salida."""
    if os.path.isfile(output_file):
        subprocess.run(['python', 'resumen.py', output_file], check=True)
