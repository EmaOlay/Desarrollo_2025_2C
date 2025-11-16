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

# Consultar el usuario
KEY_USER = "user:emaolay2"
print(f"\nConsultando clave: {KEY_USER}...")
usuario_recuperado = r.get(KEY_USER)

if menu_recuperado_json:
    # usuario = json.loads(menu_recuperado_json)
    print(f"usuario_recuperado: {usuario_recuperado}")
    print(f"TTL restante: {r.ttl(KEY_USER)} segundos")
    print("Usuario recuperado")
    print(usuario)
    # print(f"TTL restante: {r.ttl("usuario:emaolay")} segundos")
else:
    print("El usuario no se encontró en la caché o ha expirado.")


KEY_SESSION = "session:emaolay2"
print(f"\nConsultando clave: {KEY_SESSION}...")
session_recuperada = r.get(KEY_SESSION)

if session_recuperada:
    print(f"session_recuperada: {session_recuperada}")
    print(f"TTL restante: {r.ttl(KEY_SESSION)} segundos")
    print("Sesión recuperada")
else:
    print("La sesión no se encontró en la caché o ha expirado.")

print("\nScript finalizado.")