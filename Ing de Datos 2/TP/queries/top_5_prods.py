import subprocess
import json
import sys
import re # ¡Nuevo! Importamos el módulo de expresiones regulares

# --- CONFIGURACIÓN ---
MONGO_QUERY_FILE = "/app/queries/Auxiliares(no ejecutar directamente)/mongo_query_top5.js"

# --- CONFIGURACIÓN DE CONEXIÓN ---
MYSQL_CONN = "mysql -h mysql -u root -proot_password my_data_warehouse --skip-column-names --batch --skip-ssl"
MONGO_CONN = "mongosh mongodb://mongodb:27017/starbucks_transactions -u rootuser -p rootpassword --authenticationDatabase admin --quiet"

def run_command(command, input_data=None):
    """Ejecuta un comando de shell y devuelve la salida stdout o levanta un error."""
    try:
        # Usamos check_output para asegurar que el comando se ejecuta sin error
        result = subprocess.run(
            command,
            input=input_data,
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"\n--- ERROR DE EJECUCIÓN DEL COMANDO ---", file=sys.stderr)
        print(f"Comando: {e.cmd}", file=sys.stderr)
        print(f"Stderr: {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: Comando no encontrado (mysql o mongosh).", file=sys.stderr)
        sys.exit(1)


def get_sucursal_ids(pais):
    """Paso 1: Obtiene los IDs de sucursal de MySQL."""
    print(f"--- 1. Extrayendo IDs de Sucursal para el País: {pais} (MySQL) ---")
    
    # Query de MySQL para obtener los IDs
    mysql_query = f"SELECT id FROM Sucursal WHERE pais = '{pais}';"
    command = f'{MYSQL_CONN} -e "{mysql_query}"'
    
    # Ejecuta el comando y obtiene los IDs separados por salto de línea
    ids_bruto = run_command(command)
    
    if not ids_bruto:
        print(f"ERROR: No se encontraron sucursales para el país '{pais}'.")
        return []

    # Limpia y convierte la salida en una lista de IDs
    # La salida bruta puede ser '1\n5\n8'
    ids_list = [int(id_str.strip()) for id_str in ids_bruto.split('\n') if id_str.strip().isdigit()]
    print(f"IDs de Sucursal encontrados: {ids_list}")
    return ids_list

def get_top5_productos(sucursal_ids):
    """Paso 2: Ejecuta el script de agregación en MongoDB."""
    print("\n--- 2. Calculando Top 5 Productos más vendidos (MongoDB) ---")
    
    # 2a. Convertir IDs de Python a array de JavaScript
    sucursal_ids_js = json.dumps(sucursal_ids)
    
    # 2b. Leer el script de agregación de MongoDB
    with open(MONGO_QUERY_FILE, 'r') as f:
        mongo_script_content = f.read()

    # 2c. Crear el script final con la variable inyectada
    # Nota: Usamos 'var sucursalIds = [1, 5];\n' + el script de agregación
    mongo_script_with_vars = f"var sucursalIds = {sucursal_ids_js};\n{mongo_script_content}"
    
    # 2d. Ejecutar mongosh y capturar la salida
    command = f'{MONGO_CONN}'
    
    # Usamos subprocess.run con input para enviar el script al stdin de mongosh
    mongo_output = run_command(command, input_data=mongo_script_with_vars)

    # 2e. Limpiar y parsear la salida JSON (Lógica corregida para ruido de mongosh)
    productos_agrupados = []
    
    # 1. Limpieza agresiva del output de mongosh
    # Eliminar prompts y ruido que aparecen en el output
    
    # Expresión para eliminar el prompt 'starbucks_transactions>' al inicio de cualquier línea, 
    # y los puntos suspensivos '...'
    cleaned_output = re.sub(r'(^\s*starbucks_transactions>|\.{3})\s*', '', mongo_output, flags=re.MULTILINE)
    
    # 2. Encontrar todos los bloques que parecen objetos JavaScript
    # Buscamos cualquier contenido que esté entre '{' y '}' (incluyendo saltos de línea)
    js_objects_match = re.findall(r'\{(.*?)\}', cleaned_output, re.DOTALL)
    
    for js_content in js_objects_match:
        # Reconstruir el objeto, incluyendo las llaves para el parsing
        js_object_str = "{" + js_content.strip() + "}"
        
        try:
            # 3. Conversión de JS (sin comillas en claves) a JSON estricto
            # Ejemplo: {totalVendido: 3, idProducto: 2} -> {"totalVendido": 3, "idProducto": 2}
            
            # Regex para envolver las claves (palabras seguidas de ':') en comillas dobles
            json_string_safe = re.sub(r'([a-zA-Z0-9_]+)\s*:', r'"\1":', js_object_str)
            
            # Reemplazamos comillas simples que a veces aparecen por comillas dobles
            json_string_safe = json_string_safe.replace("'", '"')
            
            # Finalmente, parseamos el JSON estricto
            data = json.loads(json_string_safe)
            productos_agrupados.append(data)
            
        except json.JSONDecodeError:
            # Si falla el parseo de un bloque, lo ignoramos (podría ser un bloque vacío o un error)
            pass

    if not productos_agrupados:
        print("ERROR: MongoDB no devolvió resultados válidos. Verifique si hay datos en la colección 'Ticket'.")
        return []
        
    print(f"MongoDB devolvió {len(productos_agrupados)} productos principales.")
    return productos_agrupados


def lookup_product_names(top_products_data):
    """Paso 3: Realiza el lookup final en MySQL y combina los resultados."""
    print("\n--- 3. Lookup de Nombres de Producto y Resultados Finales (MySQL) ---")
    
    if not top_products_data:
        return

    # 3a. Obtener la lista de IDs para la cláusula IN
    product_ids = [p.get('idProducto', 0) for p in top_products_data]
    product_ids_string = ",".join(map(str, product_ids))
    
    # 3b. Obtener nombres de MySQL (solo los ID y nombres)
    mysql_query = f"SELECT id, nombre FROM Producto WHERE id IN ({product_ids_string});"
    command = f'{MYSQL_CONN} -e "{mysql_query}"'
    
    # El output de MySQL es una tabla (id, nombre)
    mysql_output = run_command(command)
    
    # 3c. Procesar la tabla de MySQL y combinar con los totales de MongoDB
    # Convertir la lista de IDs/Nombres en un diccionario para el lookup rápido
    name_map = {}
    for line in mysql_output.split('\n'):
        parts = line.split('\t')
        if len(parts) == 2 and parts[0].strip().isdigit():
            name_map[int(parts[0])] = parts[1].strip()

    # 3d. Generar el reporte final
    report = []
    for product in top_products_data:
        p_id = product['idProducto']
        report.append({
            "Rank": len(report) + 1,
            "ID_Producto": p_id,
            "Nombre": name_map.get(p_id, "Nombre no encontrado"),
            "Total_Vendido": product['totalVendido']
        })

    # Imprimir el reporte final en formato de tabla
    print("\n=======================================================")
    print(f"| TOP 5 PRODUCTOS VENDIDOS EN {PAIS_BUSCADO.upper()} |")
    print("=======================================================")
    print(f"{'Rank':<5} | {'ID':<5} | {'Nombre':<30} | {'Total Vendido':<15}")
    print("-" * 60)
    for r in report:
        print(f"{r['Rank']:<5} | {r['ID_Producto']:<5} | {r['Nombre']:<30} | {r['Total_Vendido']:<15}")
    print("=======================================================")


if __name__ == '__main__':
    # 0. Establecer el país (aquí se pediría al usuario en una TUI real)
    print("Ingrese un pais.")
    PAIS_BUSCADO = input()
    if PAIS_BUSCADO:
        # Ejecución de la lógica políglota
        sucursal_ids = get_sucursal_ids(PAIS_BUSCADO)
        
        if sucursal_ids:
            top_products = get_top5_productos(sucursal_ids)
            lookup_product_names(top_products)
        else:
            print("Proceso terminado: No se puede continuar sin IDs de sucursal.")
    else:
        print(f"El script requiere un pais. Recibi{PAIS_BUSCADO}")
