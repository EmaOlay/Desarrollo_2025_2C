import subprocess
import sys
import json
import re
import os # Import os # Import tempfile

# --- CONFIGURACIÓN ---
MONGO_QUERY_FILE = "/app/queries/Auxiliares(no ejecutar directamente)/consulta_tickets_cliente.js"
MONGO_CONN = "mongosh mongodb://mongodb:27017/starbucks_transactions -u rootuser -p rootpassword --authenticationDatabase admin --quiet"

# Configuración de MySQL
MYSQL_HOST = "mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root_password"
MYSQL_DATABASE = "my_data_warehouse"

def run_command(command, input_data=None):
    """Ejecuta un comando de shell y devuelve la salida stdout o levanta un error."""
    try:
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
        print("ERROR: Comando no encontrado (mongosh).", file=sys.stderr)
        sys.exit(1)

def validate_client_in_mysql(cliente_id):
    """Valida si un cliente_id existe en la base de datos MySQL."""
    print(f"\n--- Validando Cliente ID: {cliente_id} en MySQL ---")
    
    # Construir el comando MySQL para ejecutar la consulta directamente
    command = (
        f"mysql -h {MYSQL_HOST} -u {MYSQL_USER} -p{MYSQL_PASSWORD} "
        f"{MYSQL_DATABASE} --batch --skip-ssl -e \"SELECT COUNT(*) FROM Cliente WHERE id = {cliente_id};\""
    )
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        
        # La salida de mysql --batch para SELECT COUNT(*) es el número directamente
        # Asegurarse de que la salida no esté vacía y sea un número
        # La salida puede incluir el nombre de la columna, por lo que necesitamos limpiarla
        output_lines = result.stdout.strip().split('\n')
        if len(output_lines) > 1 and output_lines[-1].isdigit(): # Expecting header + count
            count = int(output_lines[-1])
            if count > 0:
                print(f"Cliente ID {cliente_id} encontrado en MySQL.")
                return True
            else:
                print(f"Cliente ID {cliente_id} NO encontrado en MySQL.")
                return False
        else:
            print(f"ERROR: Salida inesperada de MySQL: {result.stdout.strip()}", file=sys.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n--- ERROR DE EJECUCIÓN DE COMANDO MYSQL ---", file=sys.stderr)
        print(f"Comando: {e.cmd}", file=sys.stderr)
        print(f"Stderr: {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: Comando 'mysql' no encontrado.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR inesperado durante la validación MySQL: {e}", file=sys.stderr)
        sys.exit(1)

def get_tickets_by_client_id(cliente_id):
    """Ejecuta la consulta de MongoDB inyectando el clienteId."""
    print(f"\n--- Consultando Tickets para Cliente ID: {cliente_id} (Septiembre) ---")
    
    
    # 1. Leer el script de consulta de MongoDB
    try:
        with open(MONGO_QUERY_FILE, 'r') as f:
            mongo_script_content = f.read()
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo de consulta: {MONGO_QUERY_FILE}", file=sys.stderr)
        sys.exit(1)

    # 2. Inyectar la variable de Python en el script JS
    mongo_script_with_vars = f"var clienteId = {cliente_id};\n{mongo_script_content}"
    
    # 3. Ejecutar mongosh y capturar la salida
    command = f'{MONGO_CONN}'
    mongo_output = run_command(command, input_data=mongo_script_with_vars)

    #debug
    # print(mongo_output)
    
    # 4. Limpiar la salida y extraer solo los objetos JSON
    # Expresión regular para eliminar el prompt y el ruido de terminal
    clean_output = re.sub(r'starbucks_transactions>|\.{3}', '', mongo_output).strip()
    
    # Buscar todos los objetos de JavaScript (incluyendo los que están en múltiples líneas)
    # y convertir las claves sin comillas a claves con comillas dobles para que json.loads funcione
    js_objects = re.findall(r'\{[^{}]*\}', clean_output, re.DOTALL)
    
    tickets_encontrados = []
    
    for js_obj in js_objects:
        try:
            # Reemplazo de sintaxis JS (clave: valor) a JSON estricto ("clave": valor)
            # Esto es un patrón común en el output de printjson
            json_string = re.sub(r'(\w+):', r'"\1":', js_obj)
            data = json.loads(json_string)
            tickets_encontrados.append(data)
        except json.JSONDecodeError as e:
            # Ignorar si falla el parseo, ya que podría ser ruido que la regex no limpió
            pass

    # 5. Imprimir resultados
    if tickets_encontrados:
        print(f"\nSe encontraron {len(tickets_encontrados)} tickets en Septiembre para el cliente {cliente_id}:\n")
        
        # Imprimir la salida en un formato amigable
        for i, ticket in enumerate(tickets_encontrados):
            print(f"--- Ticket {i + 1}---")
            print(f"{ticket}")
            # Puedes añadir más detalles si es necesario
    else:
        print(f"\nNo se encontraron tickets para el cliente {cliente_id} en Septiembre.")


if __name__ == '__main__':
    # El script espera el clienteId como primer argumento de línea de comandos
    print("Ingrese un Cliente ID.")
    cliente_id_input = input()
    if cliente_id_input:
        try:
            cliente_id = int(cliente_id_input)
            if validate_client_in_mysql(cliente_id):
                get_tickets_by_client_id(cliente_id)
            else:
                print(f"Validación fallida para Cliente ID: {cliente_id}. No se consultará MongoDB.")
        except ValueError:
            print(f"ERROR: El Cliente ID debe ser un número entero. Recibido: {cliente_id_input}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Esperaba recibir un cliente_id, recibí: {cliente_id_input}", file=sys.stderr)
        sys.exit(1)