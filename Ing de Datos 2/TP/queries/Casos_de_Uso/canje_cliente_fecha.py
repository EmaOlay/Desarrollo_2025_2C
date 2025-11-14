import sys
from pymongo import MongoClient
import mysql.connector
from datetime import datetime

# --- CONFIGURACIÓN MONGODB ---
MONGO_HOST = 'mongodb'
MONGO_PORT = 27017
MONGO_DB_NAME = 'starbucks_transactions'
MONGO_USER = 'rootuser'
MONGO_PASSWORD = 'rootpassword'
MONGO_AUTH_DB = 'admin'

# --- CONFIGURACIÓN MYSQL ---
MYSQL_HOST = 'mysql'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root_password'
MYSQL_DATABASE = 'my_data_warehouse'

def get_mongodb_collection():
    """Establece y devuelve la colección 'canje' de MongoDB."""
    try:
        client = MongoClient(
            host=MONGO_HOST,
            port=MONGO_PORT,
            username=MONGO_USER,
            password=MONGO_PASSWORD,
            authSource=MONGO_AUTH_DB
        )
        db = client[MONGO_DB_NAME]
        print("Conexión a MongoDB establecida.")
        return db.canje, client # Devolver también el cliente para cerrarlo después
    except Exception as e:
        print(f"ERROR al conectar a MongoDB: {e}", file=sys.stderr)
        sys.exit(1)

def get_mysql_connection():
    """Establece y devuelve una conexión a MySQL."""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        print("Conexión a MySQL establecida.")
        return conn
    except mysql.connector.Error as e:
        print(f"ERROR al conectar a MySQL: {e}", file=sys.stderr)
        sys.exit(1)

def get_client_details_from_mysql(mysql_conn, cliente_id):
    """Busca el nombre y email de un cliente en MySQL."""
    cursor = mysql_conn.cursor()
    query = f"SELECT nombre, email FROM Cliente WHERE id = %s"
    try:
        cursor.execute(query, (cliente_id,))
        result = cursor.fetchone()
        if result:
            return {"nombre": result[0], "email": result[1]}
        return None
    except mysql.connector.Error as e:
        print(f"ERROR al consultar MySQL para cliente_id {cliente_id}: {e}", file=sys.stderr)
        return None
    finally:
        cursor.close()

def main():
    print("--- Consulta de Canjes por Cliente y Fecha ---")

    # 1. Obtener entrada del usuario
    while True:
        cliente_id_str = input("Ingrese el ID del cliente (entero): ")
        try:
            cliente_id = int(cliente_id_str)
            break
        except ValueError:
            print("ID de cliente inválido. Por favor, ingrese un número entero.")

    while True:
        fecha_str = input("Ingrese la fecha (YYYY-MM-DD): ")
        try:
            fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d')
            # Para MongoDB, necesitamos un rango de tiempo para un día específico
            fecha_inicio_dia = datetime(fecha_dt.year, fecha_dt.month, fecha_dt.day, 0, 0, 0)
            fecha_fin_dia = datetime(fecha_dt.year, fecha_dt.month, fecha_dt.day, 23, 59, 59)
            break
        except ValueError:
            print("Formato de fecha inválido. Por favor, use YYYY-MM-DD.")

    mongo_client = None
    mysql_conn = None

    try:
        # 2. Conectar a las bases de datos
        mongo_canje_collection, mongo_client = get_mongodb_collection()
        mysql_conn = get_mysql_connection()

        # 3. Consultar MongoDB
        print(f"\nConsultando MongoDB para cliente_id={cliente_id} y fecha={fecha_str}...")
        mongo_query = {
            "cliente_id": cliente_id,
            "fecha_canje": {
                "$gte": fecha_inicio_dia,
                "$lte": fecha_fin_dia
            }
        }
        
        canjes_encontrados = mongo_canje_collection.find(mongo_query)
        
        found_results = False
        for canje in canjes_encontrados:
            found_results = True
            # 4. Buscar detalles del cliente en MySQL
            client_details = get_client_details_from_mysql(mysql_conn, canje['cliente_id'])

            if client_details:
                print("\n--- Canje Encontrado ---")
                print(f"Cliente Nombre: {client_details['nombre']}")
                print(f"Cliente Email: {client_details['email']}")
                print(f"Item Canjeado: {canje.get('item_canjeado', 'N/A')}")
            else:
                print(f"\nADVERTENCIA: No se encontraron detalles de cliente en MySQL para cliente_id: {canje['cliente_id']}")
                print(f"Item Canjeado (MongoDB): {canje.get('item_canjeado', 'N/A')}")

        if not found_results:
            print(f"\nNo se encontraron canjes para el cliente {cliente_id} en la fecha {fecha_str}.")

    except Exception as e:
        print(f"ERROR durante la ejecución: {e}", file=sys.stderr)
    finally:
        if mongo_client:
            mongo_client.close()
            print("\nConexión a MongoDB cerrada.")
        if mysql_conn:
            mysql_conn.close()
            print("Conexión a MySQL cerrada.")

if __name__ == "__main__":
    main()
