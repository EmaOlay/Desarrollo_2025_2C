import redis
import json
import time
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# --- Configuración de Conexión a Bases de Datos ---

# Redis
REDIS_HOST = 'redis_cache'
REDIS_PORT = 6379
KEY_MENU_DEL_DIA = "menu_del_dia"
TTL_MENU_DEL_DIA = 3600  # 1 hora

# MySQL
MYSQL_HOST = 'mysql'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root_password'
MYSQL_DATABASE = 'my_data_warehouse'

# --- Funciones de Base de Datos ---

def get_mysql_connection():
    """Establece y devuelve una conexión a MySQL."""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def get_dynamic_menu_items(conn, branch_address='123 Main St', limit=3):
    """
    Consulta a MySQL para obtener productos aleatorios del stock de una sucursal.
    """
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.nombre, p.precio, p.tipo
        FROM Producto p
        JOIN Stock s ON p.id = s.idProducto
        JOIN Sucursal suc ON s.idSucursal = suc.id
        WHERE suc.direccion = %s AND s.cantidad > 0
        ORDER BY RAND()
        LIMIT %s;
    """
    try:
        cursor.execute(query, (branch_address, limit))
        products = cursor.fetchall()
        # Convertir Decimal a float para que sea serializable en JSON
        for prod in products:
            prod['precio'] = float(prod['precio'])
        return products
    except Error as e:
        print(f"Error al consultar productos en MySQL: {e}")
        return []
    finally:
        cursor.close()

# --- Lógica Principal ---

def main():
    """
    Genera un menú del día dinámico, lo guarda en Redis y luego lo consulta.
    """
    # 1. Conectar a Redis
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        r.ping()
        print("Conexión a Redis exitosa!")
    except redis.exceptions.ConnectionError as e:
        print(f"No se pudo conectar a Redis: {e}")
        return

    # 2. Conectar a MySQL y generar el menú
    mysql_conn = get_mysql_connection()
    menu_items = get_dynamic_menu_items(mysql_conn)

    if mysql_conn and mysql_conn.is_connected():
        mysql_conn.close()
        print("Conexión a MySQL cerrada.")

    if not menu_items:
        print("No se pudieron obtener productos para el menú del día. Usando menú de respaldo.")
        menu_items = [
            {"nombre": "Café del Día (Respaldo)", "precio": 2.50, "tipo": "Bebida Caliente"},
            {"nombre": "Croissant (Respaldo)", "precio": 2.00, "tipo": "Panadería"}
        ]

    # 3. Construir y guardar el menú en Redis
    menu_content = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "items": menu_items,
        "promocion": "¡Pregunta por nuestras ofertas especiales en caja!"
    }
    menu_json = json.dumps(menu_content)

    print(f"\nEstableciendo el menú del día dinámico en Redis (TTL: {TTL_MENU_DEL_DIA}s)...")
    r.setex(KEY_MENU_DEL_DIA, TTL_MENU_DEL_DIA, menu_json)
    print("Menú del día establecido.")

    # 4. Consultar y mostrar el menú desde Redis
    print(f"\nConsultando el menú del día (clave: {KEY_MENU_DEL_DIA})...")
    menu_recuperado_json = r.get(KEY_MENU_DEL_DIA)

    if menu_recuperado_json:
        menu_recuperado = json.loads(menu_recuperado_json)
        print("Menú del día recuperado de la caché:")
        print(json.dumps(menu_recuperado, indent=2, ensure_ascii=False))
        print(f"TTL restante: {r.ttl(KEY_MENU_DEL_DIA)} segundos")
    else:
        print("El menú del día no se encontró en la caché o ha expirado.")

    print("\nScript finalizado.")

if __name__ == "__main__":
    main()
