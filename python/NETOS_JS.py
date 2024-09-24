import pandas as pd
import os
import sys
import re

def format_code_with_underscore(code):
    """
    Formatea el código para agregar un guion bajo (_) como prefijo.
    """
    if isinstance(code, (int, str)):
        return f"_{str(code)}"
    return ''

def remove_duplicates(codes):
    """
    Elimina duplicados en la lista de códigos y mantiene el orden original.
    """
    seen = set()
    unique_codes = []
    for code in codes:
        if code not in seen:
            seen.add(code)
            unique_codes.append(code)
    return unique_codes

def process_excel_file(file_path):
    """
    Función para procesar el archivo Excel y extraer las asignaciones de NET, SUBNET y NET3.
    """
    xl = pd.ExcelFile(file_path)
    sheet_names = xl.sheet_names
    print(f"Sheet names found in Excel file: {sheet_names}")

    all_net_mapping = {}
    all_subnet_mapping = {}
    all_net3_mapping = {}

    for sheet_name in sheet_names:
        print(f"\nProcessing sheet: {sheet_name}")
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)  # No asumir la primera fila como encabezado

        # Encontrar la fila que contiene los encabezados (header)
        header_row = None
        for i, row in df.iterrows():
            if 'Código' in str(row.values):
                header_row = i
                break
        
        if header_row is None:
            print(f"Warning: Header not found in sheet {sheet_name}. Skipping.")
            continue
        
        df.columns = df.iloc[header_row]  # Establecer el encabezado correctamente

        net_mapping = {}
        subnet_mapping = {}
        net3_mapping = {}

        current_net = None
        current_subnet = None
        current_net3 = None

        net_codes = set()
        net2_codes = set()

        for index, row in df.iterrows():
            code = row.get('Código')
            net1 = row.get('net1')
            net2 = row.get('net2')
            net3 = row.get('net3')
            net4 = row.get('net4')

            print(f"\nProcessing row {index} in sheet {sheet_name}:")
            print(f"Code: {code}, net1: {net1}, net2: {net2}, net3: {net3}, net4: {net4}")

            if pd.notna(code) and isinstance(code, (int, str)):
                if pd.notna(net1):
                    # Reset current_subnet and current_net3 when a new NET is identified
                    current_net = code
                    net_codes.add(code)
                    if current_net not in net_mapping:
                        net_mapping[current_net] = []
                    print(f"NET identified: {current_net} -> {net1}")
                    current_subnet = None
                    current_net3 = None

                if pd.notna(net2) and 'SUBNET' in str(net2).upper():
                    current_subnet = code
                    net2_codes.add(code)
                    if current_subnet not in subnet_mapping:
                        subnet_mapping[current_subnet] = []
                    print(f"SUBNET identified: {current_subnet} -> {net2}")

                if pd.notna(net3) and pd.isna(net4):
                    current_net3 = code
                    if current_net3 not in net3_mapping:
                        net3_mapping[current_net3] = []
                    print(f"NET3 identified: {current_net3} -> {net3}")

                # Add code to the current NET, SUBNET, or NET3 mapping
                if current_net:
                    net_mapping[current_net].append(code)
                    print(f"Added code {code} to NET {current_net}")
                if current_subnet:
                    subnet_mapping[current_subnet].append(code)
                    print(f"Added code {code} to SUBNET {current_subnet}")
                if current_net3:
                    net3_mapping[current_net3].append(code)
                    print(f"Added code {code} to NET3 {current_net3}")

        all_net_mapping[sheet_name] = net_mapping
        all_subnet_mapping[sheet_name] = subnet_mapping
        all_net3_mapping[sheet_name] = net3_mapping

    return all_net_mapping, all_subnet_mapping, all_net3_mapping

def generate_output(all_net_mapping, all_subnet_mapping, all_net3_mapping):
    output = []

    for sheet_name, net_mapping in all_net_mapping.items():
        # NET section
        output.append(f"\n'# Sheet: {sheet_name}")
        output.append("'*******************************************************************************************************************************************************************************************************************************************************************************************************'")
        output.append(f"'NET_{sheet_name}'")
        output.append("'*******************************************************************************************************************************************************************************************************************************************************************************************************'")
        if net_mapping:
            for net_code, codes in net_mapping.items():
                if codes:
                    formatted_codes = remove_duplicates(map(format_code_with_underscore, sorted(set(codes))))
                    formatted_codes_str = ', '.join(formatted_codes)
                    if len(codes) > 1 or list(codes)[0] != net_code:
                        output.append(f'{sheet_name}= sumarnet_subnets(dmgrglobal, {sheet_name}, "", "", {{{formatted_codes_str}}}, {{{format_code_with_underscore(net_code)}}}, "_")')
                        print(f"Generated NET line for sheet {sheet_name}: {output[-1]}")

        # SUBNET section
        output.append("'*******************************************************************************************************************************************************************************************************************************************************************************************************'")
        output.append(f"'SUBNET_{sheet_name}'")
        output.append("'*******************************************************************************************************************************************************************************************************************************************************************************************************'")
        subnet_mapping = all_subnet_mapping.get(sheet_name, {})
        if subnet_mapping:
            for subnet, codes in subnet_mapping.items():
                filtered_codes = [code for code in codes if code not in all_net_mapping.get(sheet_name, {}).keys()]
                if filtered_codes:
                    formatted_codes = remove_duplicates(map(format_code_with_underscore, sorted(set(filtered_codes))))
                    formatted_codes_str = ', '.join(formatted_codes)
                    if len(filtered_codes) > 1 or filtered_codes[0] != subnet:
                        output.append(f'{sheet_name}= sumarnet_subnets(dmgrglobal, {sheet_name}, "", "", {{{formatted_codes_str}}}, {{{format_code_with_underscore(subnet)}}}, "_")')
                        print(f"Generated SUBNET line for sheet {sheet_name}: {output[-1]}")

        # NET3 section
        output.append("'*******************************************************************************************************************************************************************************************************************************************************************************************************'")
        output.append(f"'NET3_{sheet_name}'")
        output.append("'*******************************************************************************************************************************************************************************************************************************************************************************************************'")
        net3_mapping = all_net3_mapping.get(sheet_name, {})
        if net3_mapping:
            for net3_code, codes in net3_mapping.items():
                filtered_codes = [code for code in codes if code not in (all_net_mapping.get(sheet_name, {}).keys() | all_subnet_mapping.get(sheet_name, {}).keys())]
                if filtered_codes:
                    formatted_codes = remove_duplicates(map(format_code_with_underscore, sorted(set(filtered_codes))))
                    formatted_codes_str = ', '.join(formatted_codes)
                    if len(filtered_codes) > 1 or filtered_codes[0] != net3_code:
                        output.append(f'{sheet_name}= sumarnet_subnets(dmgrglobal, {sheet_name}, "", "", {{{formatted_codes_str}}}, {{{format_code_with_underscore(net3_code)}}}, "_")')
                        print(f"Generated NET3 line for sheet {sheet_name}: {output[-1]}")

    return "\n".join(output)

def remove_redundant_codes(file_path):
    """
    Revisa el archivo TXT generado y elimina los códigos redundantes en las primeras llaves si están presentes en las segundas llaves.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    output_lines = []
    
    # Regexp patterns to capture the necessary parts
    pattern = re.compile(r'(\w+)= sumarnet_subnets\(dmgrglobal, \1, "", "", \{(.+?)\}, \{(.+?)\}, "_"')
    
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            section_name = match.group(1)
            first_brace_contents = set(match.group(2).split(', '))
            second_brace_contents = set(match.group(3).split(', '))
            
            # Remove codes in the second brace from the first brace
            updated_first_brace_contents = first_brace_contents - second_brace_contents
            updated_first_brace_contents_str = ', '.join(sorted(updated_first_brace_contents, key=lambda x: int(x.lstrip('_')) if x.lstrip('_').isdigit() else x))
            
            # Reconstruct the line with updated contents
            new_line = f'{section_name}= sumarnet_subnets(dmgrglobal, {section_name}, "", "", {{{updated_first_brace_contents_str}}}, {{{", ".join(sorted(second_brace_contents))}}}, "_")\n'
            output_lines.append(new_line)
        else:
            output_lines.append(line)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(output_lines)

def main():
    """
    Función principal para ejecutar el programa.
    """
    if len(sys.argv) < 2:
        print("No input file provided.")
        return

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"File {file_path} does not exist.")
        return

    all_net_mapping, all_subnet_mapping, all_net3_mapping = process_excel_file(file_path)
    output = generate_output(all_net_mapping, all_subnet_mapping, all_net3_mapping)

    if output:
        output_file_path = file_path.replace('.xlsx', '.txt')
        with open(output_file_path, 'w') as f:
            f.write(output)
        print(f"El archivo 'logica_de_netos.txt' ha sido generado en: {output_file_path}")
        
        # Llamar a la función para eliminar códigos redundantes
        remove_redundant_codes(output_file_path)
        print(f"Se ha limpiado el archivo para eliminar códigos redundantes.")
    else:
        print("No output generated.")

if __name__ == "__main__":
    main()