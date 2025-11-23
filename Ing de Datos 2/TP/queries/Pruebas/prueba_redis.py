import redis
import json

def test_redis_connection_and_data():
    """
    Se conecta a Redis, verifica la conexión y muestra todas las claves y sus valores.
    """
    try:
        # Conexión al servidor de Redis
        r = redis.Redis(host='redis_cache', port=6379, db=0, decode_responses=True)
        r.ping()
        print("--- Conexión a Redis exitosa ---\n")
    except redis.exceptions.ConnectionError as e:
        print(f"Error: No se pudo conectar a Redis en 'redis_cache:6379'.")
        print(f"Detalle: {e}")
        print("Asegúrate de que el contenedor de Redis esté corriendo y sea accesible.")
        return

    # Obtener información del servidor
    info = r.info()
    print("--- Información del Servidor ---")
    print(f"Versión de Redis: {info.get('redis_version')}")
    print(f"Memoria Usada: {info.get('used_memory_human')}")
    print(f"Número de Claves: {info.get('db0', {}).get('keys', 'N/A')}\n")

    # Escanear y mostrar todas las claves
    print("--- Contenido de la Base de Datos (Clave por Clave) ---")
    keys = r.keys('*')
    if not keys:
        print("La base de datos de Redis está vacía.")
    else:
        for key in keys:
            key_type = r.type(key)
            ttl = r.ttl(key)
            ttl_str = f"(TTL: {ttl}s)" if ttl != -1 else "(Sin expiración)"

            print(f"\n> Clave: '{key}' | Tipo: {key_type} {ttl_str}")

            try:
                if key_type == 'string':
                    value = r.get(key)
                    # Intentar decodificar como JSON para una mejor visualización
                    try:
                        parsed_json = json.loads(value)
                        print("  Valor (JSON):")
                        print(json.dumps(parsed_json, indent=2))
                    except (json.JSONDecodeError, TypeError):
                        print(f"  Valor: {value}")
                
                elif key_type == 'hash':
                    value = r.hgetall(key)
                    print("  Valor (Hash):")
                    for field, val in value.items():
                        print(f"    - {field}: {val}")
                
                elif key_type == 'list':
                    value = r.lrange(key, 0, -1)
                    print(f"  Valor (Lista, {len(value)} elementos): {value}")

                elif key_type == 'set':
                    value = r.smembers(key)
                    print(f"  Valor (Set, {len(value)} elementos): {value}")

                elif key_type == 'zset':
                    value = r.zrange(key, 0, -1, withscores=True)
                    print(f"  Valor (Sorted Set, {len(value)} elementos): {value}")

                else:
                    print(f"  (Tipo de dato '{key_type}' no manejado para visualización detallada)")

            except Exception as e:
                print(f"  Error al obtener el valor de la clave '{key}': {e}")

    print("\n--- Fin del script de prueba de Redis ---")

if __name__ == "__main__":
    test_redis_connection_and_data()