import os
import sys
import redis
import getpass
import hashlib
from rich.console import Console
from rich.table import Table
from neo4j import GraphDatabase # Importar la librería de Neo4j

console = Console()
QUERIES_DIR = "/app/queries"

# --- CONFIGURACIÓN REDIS ---
REDIS_HOST = "redis"
REDIS_PORT = 6379

# --- CONFIGURACIÓN NEO4J ---
NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jpassword"

# --- FUNCIONES DE HASHING ---
def hash_password(password, salt=None):
    """Hashea una contraseña con un salt. Si no se provee salt, se genera uno."""
    if salt is None:
        salt = os.urandom(16)
    
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    
    return f"{salt.hex()}:{hashed_password}"

def verify_password(stored_password_hash, provided_password):
    """Verifica si la contraseña proveída coincide con el hash almacenado."""
    try:
        salt_hex, hashed_password = stored_password_hash.split(':')
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False

    salted_provided_password = salt + provided_password.encode('utf-8')
    hashed_provided_password = hashlib.sha256(salted_provided_password).hexdigest()
    
    return hashed_provided_password == hashed_password

# --- LÓGICA DE SESIÓN Y AUTENTICACIÓN ---
def get_redis_connection():
    """Crea y retorna una conexión a Redis."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        r.ping()
        console.print("[bold green]Conexión con Redis establecida.[/bold green]")
        return r
    except redis.exceptions.ConnectionError as e:
        console.print(f"[bold red]Error de conexión con Redis:[/bold red] {e}")
        return None

def handle_auth_and_session(redis_conn, username, password):
    """
    Gestiona la autenticación y sesión del usuario.
    Retorna True si el usuario está autenticado y la sesión activa, False en caso contrario.
    """
    if not redis_conn:
        console.print("[bold red]No se puede gestionar la sesión sin conexión a Redis.[/bold red]")
        return False

    session_key = f"session:{username}"
    user_key = f"user:{username}"

    # 1. Validar si la sesión está activa
    if redis_conn.exists(session_key):
        ttl = redis_conn.ttl(session_key)
        console.print(f"[green]Sesión activa para [bold]{username}[/bold]. Tiempo restante: {ttl} segundos.[/green]")
        return True
    
    console.print("[yellow]Sesión no encontrada o expirada. Se requiere autenticación...[/yellow]")
    
    # 2. Si no hay sesión, autenticar al usuario
    stored_hash = redis_conn.get(user_key)
    
    if stored_hash:
        # Usuario existe, verificar contraseña
        if verify_password(stored_hash, password):
            console.print("[green]Autenticación exitosa.[/green]")
            console.print("[cyan]Creando nueva sesión de 5 minutos...[/cyan]")
            redis_conn.setex(session_key, 300, "active")
            return True
        else:
            console.print("[bold red]Autenticación fallida: Contraseña incorrecta.[/bold red]")
            return False
    else:
        # Usuario no existe, registrarlo
        console.print(f"[cyan]Usuario [bold]{username}[/bold] no registrado. Creando nuevo usuario...[/cyan]")
        new_hash = hash_password(password)
        redis_conn.set(user_key, new_hash)
        console.print("[green]Usuario registrado exitosamente.[/green]")
        
        console.print("[cyan]Creando nueva sesión de 5 minutos...[/cyan]")
        redis_conn.setex(session_key, 300, "active")
        return True

def execute_neo4j_query(file_path):
    """Ejecuta una o varias consultas Cypher desde un archivo usando la librería neo4j-driver."""
    try:
        with open(file_path, 'r') as f:
            full_query_content = f.read()

        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session() as session:
            console.print(f"[bold blue]Ejecutando consultas Cypher desde {file_path}...[/bold blue]")
            
            queries = [
                stmt.strip() for stmt in full_query_content.split(';') 
                if stmt.strip() and not stmt.strip().startswith('//') and not stmt.strip().startswith('--')
            ]

            if not queries:
                console.print("[bold yellow]El archivo Cypher no contiene consultas válidas.[/bold yellow]")
                driver.close()
                return

            for i, query in enumerate(queries):
                console.print(f"\n[bold magenta]--- Ejecutando Consulta {i+1} ---[/bold magenta]")
                console.print(f"[dim]{query}[/dim]")
                
                result = session.run(query)
                
                if result.peek():
                    table = Table(title=f"Resultados de Neo4j (Consulta {i+1})", show_lines=True)
                    for key in result.keys():
                        table.add_column(key, style="cyan")
                    
                    for record in result:
                        table.add_row(*[str(record[key]) for key in result.keys()])
                    console.print(table)
                else:
                    console.print("[bold yellow]Consulta ejecutada, no se retornaron resultados.[/bold yellow]")
        
        driver.close()
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Archivo Cypher no encontrado: {file_path}")
    except Exception as e:
        console.print(f"[bold red]Error al ejecutar consulta Neo4j:[/bold red] {e}")

# Mapeo de extensión a comando de ejecución y alias de DB
EXECUTOR_MAP = {
    ".sql": {
        "cmd": "mysql -h mysql -u root -proot_password my_data_warehouse --batch --table --skip-ssl < {file}",
        "db": "MySQL"
    },
    ".js": {
        "cmd": "mongosh mongodb://mongodb:27017/starbucks_transactions -u rootuser -p rootpassword --authenticationDatabase admin --file {file} --quiet",
        "db": "MongoDB"
    },
    ".cql": {
        "cmd": "cqlsh cassandra -f {file}",
        "db": "Cassandra"
    },
    ".cypher": {
        "handler": execute_neo4j_query,
        "db": "Neo4j"
    },
    ".py": {"cmd": "python3 {file}", "db": "Python Lógica Políglota"},
    ".sh": {
        "cmd": "sh {file}", 
        "db": "Shell Script" 
    },
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_items_in_current_dir(current_path):
    """Obtiene la lista de carpetas y archivos en el directorio actual."""
    items = []
    
    try:
        content = [name for name in os.listdir(current_path) if not name.startswith('.')]
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Directorio no encontrado: {current_path}")
        return []

    if os.path.realpath(current_path) != os.path.realpath(QUERIES_DIR):
        items.append(("..", "DIR", "[ Ir a Padre ]")) 

    dirs = []
    files = []
    
    for name in content:
        full_path = os.path.join(current_path, name)
        if os.path.isdir(full_path):
            dirs.append((name, "DIR", "Directorio")) 
        elif os.path.isfile(full_path):
            ext = os.path.splitext(name)[1].lower()
            db_alias = EXECUTOR_MAP.get(ext, {}).get("db", "Desconocida")
            files.append((name, ext, db_alias))
            
    items.extend(sorted(dirs, key=lambda x: x[0]))
    items.extend(sorted(files, key=lambda x: x[0]))
    
    return items

def run_tui():
    clear_screen()
    
    console.print("[bold cyan]Bienvenido a la CLI de Consultas 🚀[/bold cyan]")
    username = console.input("Por favor, ingrese su nombre de usuario: ").strip()
    password = getpass.getpass("Ingrese su contraseña: ").strip()
    
    redis_conn = get_redis_connection()
    if not redis_conn:
        console.print("[bold red]No se pudo conectar a Redis. La CLI no puede continuar.[/bold red]")
        return

    current_path = os.path.realpath(QUERIES_DIR)
    
    if not os.path.isdir(current_path):
        console.print(f"[bold red]Error:[/bold red] Directorio de consultas no encontrado en {QUERIES_DIR}.")
        return

    while True:
        clear_screen()
        console.print("[bold cyan]☕ Starbucks Políglota - Consola de Ejecución 🚀[/bold cyan]")
        console.print(f"[dim]Ubicación actual: /queries/{os.path.relpath(current_path, QUERIES_DIR)}[/dim]\n")

        items = get_items_in_current_dir(current_path)

        table = Table(title="Scripts y Directorios Disponibles", show_lines=True)
        table.add_column("ID", style="dim", width=4)
        table.add_column("Nombre", style="bold green")
        table.add_column("Tipo / DB", style="yellow")
        
        for i, item in enumerate(items):
            table.add_row(str(i + 1), item[0], item[2])

        console.print(table)
        console.print("\n[bold]Escriba el ID de la opción para ejecutar/navegar, o 'q' para salir.[/bold]")

        choice = console.input("Selección: ").strip()

        if choice.lower() == 'q':
            break

        try:
            index = int(choice) - 1
            if 0 <= index < len(items):
                selected_name, item_type, _ = items[index]
                
                if item_type == "DIR":
                    if selected_name == "..":
                        new_path = os.path.dirname(current_path)
                        if os.path.realpath(new_path) >= os.path.realpath(QUERIES_DIR):
                             current_path = new_path
                    else:
                        current_path = os.path.join(current_path, selected_name)
                        
                else: 
                    selected_script = selected_name
                    ext = item_type
                    executor = EXECUTOR_MAP.get(ext)
                    
                    if executor:
                        # --- INICIO: Validación de Sesión y Autenticación ---
                        if not handle_auth_and_session(redis_conn, username, password):
                            console.input("\n[bold yellow]Fallo de autenticación. Presione ENTER para reintentar...[/bold yellow]")
                            # Pedir credenciales de nuevo
                            username = console.input("Por favor, ingrese su nombre de usuario: ").strip()
                            password = getpass.getpass("Ingrese su contraseña: ").strip()
                            continue # Vuelve al inicio del bucle
                        # --- FIN: Validación ---

                        full_path = os.path.join(current_path, selected_script)
                        
                        console.print(f"\n[bold blue]>>> Ejecutando {selected_script} en {executor['db']}...[/bold blue]")
                        
                        if executor.get("handler"):
                            executor["handler"](full_path)
                        else:
                            command = executor["cmd"].format(file=full_path)
                            print(command)
                            os.system(command) 
                        
                        console.input("\n[bold yellow]Presione ENTER para continuar...[/bold yellow]")
                    else:
                        console.print("[bold red]Error:[/bold red] Extensión de archivo no soportada.")
                        console.input("\n[bold yellow]Presione ENTER para continuar...[/bold yellow]")
            else:
                console.print("[bold red]Error:[/bold red] ID no válido.")
                console.input("\n[bold yellow]Presione ENTER para continuar...[/bold yellow]")
        except ValueError:
            console.print("[bold red]Error:[/bold red] Por favor, ingrese un número o 'q'.")
            console.input("\n[bold yellow]Presione ENTER para continuar...[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]Error de ejecución:[/bold red] {e}")
            console.input("\n[bold yellow]Presione ENTER para continuar...[/bold yellow]")

    console.print("[bold green]¡Saliendo de la TUI! Hasta pronto. 👋[/bold green]")


if __name__ == "__main__":
    run_tui()