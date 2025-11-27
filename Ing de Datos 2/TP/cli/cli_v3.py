import os
import sys
import time
import random
import threading
import traceback
from rich.console import Console
import requests
import json

# Intentamos importar cli_v2 (el archivo no debe modificarse)
console = Console()
try:
    import cli_v2
except Exception:
    # Intentar cargar como módulo desde la misma carpeta (si ejecutas desde otro cwd)
    import importlib.util
    here = os.path.dirname(__file__)
    spec = importlib.util.spec_from_file_location('cli_v2', os.path.join(here, 'cli_v2.py'))
    cli_v2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli_v2)


GEN_INTERVAL = 10 # Interval in seconds


def call_seed_service():
    """Calls the /generate-order endpoint of the seed_service."""
    try:
        resp = requests.post('http://seed_service:8000/generate-order', timeout=5)
        if resp.status_code == 200:
            pass
            # console.print("[green]Successfully called seed_service to generate and insert an order.[/green]")
        else:
            console.print(f"[yellow]Warning: seed_service returned status {resp.status_code}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error calling seed_service: {e}[/red]")


def generator_loop():
    """Continuously calls the seed service to generate orders."""
    console.print("[cyan]Starting background order generator loop...[/cyan]")
    # Initial burst
    for _ in range(3):
        call_seed_service()
        time.sleep(1)

    while True:
        call_seed_service()
        time.sleep(GEN_INTERVAL)


def start_background_generator():
    """Starts the background order generator thread."""
    t = threading.Thread(target=generator_loop, daemon=True)
    t.start()


def run():
    """Starts the background generator and then launches the TUI from cli_v2."""
    try:
        # Initialize db clients from cli_v2, as the TUI might need them.
        if hasattr(cli_v2, 'init_db_clients'):
            cli_v2.init_db_clients()
    except Exception as e:
        console.print(f"[yellow]Could not initialize DB clients from cli_v2: {e}[/yellow]")
    
    # Start the background generator that calls the seed_service
    start_background_generator()

    # Run the original TUI from cli_v2
    try:
        cli_v2.run_tui()
    except Exception as e:
        console.print(f"[red]Error launching TUI from cli_v2: {e}\n{traceback.format_exc()}[/red]")


if __name__ == '__main__':
    run()
