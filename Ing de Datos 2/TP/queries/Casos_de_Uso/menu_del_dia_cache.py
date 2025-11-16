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
TTL_MENU_DEL_DIA = 60 * 60  # 1 hora en segundos

# Contenido del menú del día
menu_content = {
    "fecha": "2025-11-16",
    "items": [
        {"nombre": "Latte Especial", "precio": 5.00, "tipo": "Bebida Caliente"},
        {"nombre": "Sandwich de Autor", "precio": 8.50, "tipo": "Comida"},
        {"nombre": "Muffin de Arándanos", "precio": 3.20, "tipo": "Panadería/Pasteleria"}
    ],
    "promocion": "2x1 en Lattes de 14:00 a 16:00"
}

# Convertir el diccionario a una cadena JSON
menu_json = json.dumps(menu_content)

print(f"\nEstableciendo el menú del día en Redis con TTL de {TTL_MENU_DEL_DIA} segundos...")
r.setex(KEY_MENU_DEL_DIA, TTL_MENU_DEL_DIA, menu_json)
print("Menú del día establecido.")

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
