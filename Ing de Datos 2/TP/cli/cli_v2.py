import os
import sys
from rich.console import Console
from rich.table import Table

console = Console()
QUERIES_DIR = "/app/queries"

# Mapeo de extensión a comando de ejecución y alias de DB
EXECUTOR_MAP = {
    ".sql": {
        # MySQL ahora usa el redireccionamiento '<'
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
        "cmd": "QUERY=$(cat {file}); printf '{\"statements\": [{ \"statement\": \"%s\" }]}' \"$QUERY\" | curl -s -X POST -H 'Content-Type: application/json' -u neo4j:neo4jpassword 'http://neo4j:7474/db/neo4j/tx/commit' -d @-",
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
        # Listar contenido, ignorando archivos ocultos
        content = [name for name in os.listdir(current_path) if not name.startswith('.')]
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Directorio no encontrado: {current_path}")
        return []

    # 1. Agregar opción para subir de nivel, si no estamos en la raíz
    if os.path.realpath(current_path) != os.path.realpath(QUERIES_DIR):
        # El tercer elemento (alias) es la descripción para la tabla
        items.append(("..", "DIR", "[ Ir a Padre ]")) 

    # 2. Separar directorios de archivos
    dirs = []
    files = []
    
    for name in content:
        full_path = os.path.join(current_path, name)
        if os.path.isdir(full_path):
            # (nombre, tipo, alias)
            dirs.append((name, "DIR", "Directorio")) 
        elif os.path.isfile(full_path):
            ext = os.path.splitext(name)[1].lower()
            db_alias = EXECUTOR_MAP.get(ext, {}).get("db", "Desconocida")
            files.append((name, ext, db_alias))
            
    # Listar primero los directorios, luego los archivos, ambos ordenados alfabéticamente
    items.extend(sorted(dirs, key=lambda x: x[0]))
    items.extend(sorted(files, key=lambda x: x[0]))
    
    return items

def run_tui():
    clear_screen()
    
    # Inicializar el directorio actual, usando realpath para comparaciones seguras
    current_path = os.path.realpath(QUERIES_DIR)
    
    if not os.path.isdir(current_path):
        console.print(f"[bold red]Error:[/bold red] Directorio de consultas no encontrado en {QUERIES_DIR}.")
        return

    while True:
        clear_screen()
        console.print("[bold cyan]☕ Starbucks Políglota - Consola de Ejecución 🚀[/bold cyan]")
        # Muestra la ruta relativa para mayor claridad
        console.print(f"[dim]Ubicación actual: /queries/{os.path.relpath(current_path, QUERIES_DIR)}[/dim]\n")

        # 1. Obtener y mostrar las opciones
        items = get_items_in_current_dir(current_path)

        table = Table(title="Scripts y Directorios Disponibles", show_lines=True)
        table.add_column("ID", style="dim", width=4)
        table.add_column("Nombre", style="bold green")
        table.add_column("Tipo / DB", style="yellow")
        
        for i, item in enumerate(items):
            # item is: (name, type/ext, db_alias/description)
            table.add_row(str(i + 1), item[0], item[2])

        console.print(table)
        console.print("\n[bold]Escriba el ID de la opción para ejecutar/navegar, o 'q' para salir.[/bold]")

        # 2. Leer la Selección
        choice = console.input("Selección: ").strip()

        if choice.lower() == 'q':
            break

        try:
            index = int(choice) - 1
            if 0 <= index < len(items):
                selected_name, item_type, _ = items[index]
                
                # --- Lógica de Navegación vs. Ejecución ---
                
                if item_type == "DIR":
                    if selected_name == "..":
                        # Subir de nivel
                        new_path = os.path.dirname(current_path)
                        # Asegurar que no subimos más allá de la raíz de QUERIES_DIR
                        if os.path.realpath(new_path) >= os.path.realpath(QUERIES_DIR):
                             current_path = new_path
                        # El mensaje de error ya se maneja en get_items_in_current_dir al no incluir '..'
                    else:
                        # Entrar en la carpeta
                        current_path = os.path.join(current_path, selected_name)
                        
                else: # Es un archivo ejecutable
                    selected_script = selected_name
                    ext = item_type
                    executor = EXECUTOR_MAP.get(ext)
                    
                    if executor:
                        full_path = os.path.join(current_path, selected_script)
                        command = executor["cmd"].format(file=full_path)
                        
                        console.print(f"\n[bold blue]>>> Ejecutando {selected_script} en {executor['db']}...[/bold blue]")
                        print(command)
                        
                        # Ejecutar el comando en el shell del contenedor
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