import redis
import json
import time

# Conectar a Redis
# Asume que Redis está corriendo en localhost:6379
try:
    r = redis.Redis(host='redis_cache', port=6379, db=0)
    r.ping()
    print("Conexión a Redis exitosa!")
except redis.exceptions.ConnectionError as e:
    print(f"No se pudo conectar a Redis: {e}")
    print("Asegúrate de que el servidor Redis esté corriendo.")
    exit()

KEY_MENU_DEL_DIA = "menu_del_dia"

# Consultar el menú del día
print(f"\nConsultando el menú del día (clave: {KEY_MENU_DEL_DIA})...")
menu_recuperado_json = r.get(KEY_MENU_DEL_DIA)

if menu_recuperado_json:
    menu_recuperado = json.loads(menu_recuperado_json)
    print("Menú del día recuperado:")
    print(json.dumps(menu_recuperado, indent=2))
    print(f"TTL restante: {r.ttl(KEY_MENU_DEL_DIA)} segundos")
else:
    print("El menú del día no se encontró en la caché o ha expirado.")

print("\nScript finalizado.")
