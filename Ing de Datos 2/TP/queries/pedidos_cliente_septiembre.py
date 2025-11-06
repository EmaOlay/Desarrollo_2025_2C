import subprocess
import sys
import json
import re

# --- CONFIGURACIÓN ---
MONGO_QUERY_FILE = "/app/queries/Auxiliares(no ejecutar directamente)/consulta_tickets_cliente.js"
MONGO_CONN = "mongosh mongodb://mongodb:27017/starbucks_transactions -u rootuser -p rootpassword --authenticationDatabase admin --quiet"

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
    cliente_id = input()
    if cliente_id:
        get_tickets_by_client_id(cliente_id)
    else:
        print(f"Esperoba recibir un cliente_id, recibi: {cliente_id}")