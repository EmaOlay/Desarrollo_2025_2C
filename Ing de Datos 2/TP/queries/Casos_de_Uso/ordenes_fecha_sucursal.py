import sys
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from pymongo import MongoClient
from datetime import datetime

# --- CONFIGURACIÓN CASSANDRA ---
CASSANDRA_CONTACT_POINTS = ['cassandra']
CASSANDRA_PORT = 9042
CASSANDRA_KEYSPACE = 'starbucks_analytics'
CASSANDRA_USER = 'cassandra'
CASSANDRA_PASSWORD = 'cassandra_password'

# --- CONFIGURACIÓN MONGODB ---
MONGO_HOST = 'mongodb'
MONGO_PORT = 27017
MONGO_DB_NAME = 'starbucks_transactions'
MONGO_USER = 'rootuser'
MONGO_PASSWORD = 'rootpassword'
MONGO_AUTH_DB = 'admin'

def get_cassandra_session():
    """Establece y devuelve una sesión de Cassandra."""
    try:
        auth_provider = PlainTextAuthProvider(CASSANDRA_USER, CASSANDRA_PASSWORD)
        cluster = Cluster(CASSANDRA_CONTACT_POINTS, port=CASSANDRA_PORT, auth_provider=auth_provider)
        session = cluster.connect(CASSANDRA_KEYSPACE)
        print("Conexión a Cassandra establecida.")
        return session
    except Exception as e:
        print(f"ERROR al conectar a Cassandra: {e}", file=sys.stderr)
        sys.exit(1)

def get_mongodb_collection():
    """Establece y devuelve la colección 'ticket' de MongoDB."""
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
        return db.ticket
    except Exception as e:
        print(f"ERROR al conectar a MongoDB: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    print("--- Consulta de Órdenes por Fecha y Sucursal ---")

    # 1. Obtener entrada del usuario
    while True:
        sucursal_id_str = input("Ingrese el ID de la sucursal (entero): ")
        try:
            sucursal_id = int(sucursal_id_str)
            break
        except ValueError:
            print("ID de sucursal inválido. Por favor, ingrese un número entero.")

    while True:
        fecha_str = input("Ingrese la fecha (YYYY-MM-DD): ")
        try:
            # Cassandra espera timestamp, pero para la consulta podemos usar un rango
            # Convertimos a datetime para validación y luego a string para CQL
            fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d')
            # Para Cassandra, necesitamos un rango de tiempo para un día específico
            fecha_inicio_dia = fecha_dt.strftime('%Y-%m-%d %H:%M:%S%z') # Start of day
            fecha_fin_dia = (fecha_dt.replace(hour=23, minute=59, second=59)).strftime('%Y-%m-%d %H:%M:%S%z') # End of day
            break
        except ValueError:
            print("Formato de fecha inválido. Por favor, use YYYY-MM-DD.")

    cassandra_session = None
    mongo_ticket_collection = None

    try:
        # 2. Conectar a las bases de datos
        cassandra_session = get_cassandra_session()
        mongo_ticket_collection = get_mongodb_collection()

        # 3. Consultar Cassandra
        print(f"\nConsultando Cassandra para sucursal_id={sucursal_id} y fecha={fecha_str}...")
        # La consulta debe usar el PRIMARY KEY (idSucursal, fecha)
        # Para filtrar por un día completo, necesitamos un rango de fecha
        cql_query = f"""
            SELECT idSucursal, fecha, ticket_num
            FROM HistorialCompra
            WHERE idSucursal = {sucursal_id}
            AND fecha >= '{fecha_dt.strftime('%Y-%m-%d 00:00:00+0000')}'
            AND fecha <= '{fecha_dt.strftime('%Y-%m-%d 23:59:59+0000')}';
        """
        cassandra_rows = cassandra_session.execute(cql_query)
        
        found_matches = False
        for row in cassandra_rows:
            # print(row)

            # 4. Buscar en MongoDB
            # MongoDB fecha es ISODate, Cassandra fecha es timestamp.
            # Convertir la fecha de Cassandra a un rango para MongoDB
            # Cassandra fecha es un objeto datetime, ya podemos usarlo directamente
            mongo_query = {
                "sucursal_id": row.idsucursal,
                "fecha": {
                    "$gte": datetime(row.fecha.year, row.fecha.month, row.fecha.day, row.fecha.hour, row.fecha.minute, row.fecha.second),
                    "$lte": datetime(row.fecha.year, row.fecha.month, row.fecha.day, row.fecha.hour, row.fecha.minute, row.fecha.second)
                },
                "ticket_id": row.ticket_num
            }
            
            mongo_ticket = mongo_ticket_collection.find_one(mongo_query)

            if mongo_ticket:
                found_matches = True
                print("\n--- Coincidencia Encontrada ---")
                print(f"MongoDB _id: {mongo_ticket['_id']}")
                print(f"""Cassandra Data: 
                sucursal = {row.idsucursal}
                fecha = {row.fecha}
                ticket num = {row.ticket_num}""")
            # else:
            #     print(f"No se encontró coincidencia en MongoDB para Cassandra ticket_num={row.ticket_num}")

        if not found_matches:
            print(f"\nNo se encontraron coincidencias en MongoDB para los registros de Cassandra de la sucursal {sucursal_id} en la fecha {fecha_str}.")

    except Exception as e:
        print(f"ERROR durante la ejecución: {e}", file=sys.stderr)
    finally:
        if cassandra_session:
            cassandra_session.shutdown()
            print("\nConexión a Cassandra cerrada.")
        if 'client' in locals() and client:
            client.close()
            print("Conexión a MongoDB cerrada.")

if __name__ == "__main__":
    main()
