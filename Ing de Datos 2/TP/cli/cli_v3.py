import os
import sys
import time
import random
import threading
import traceback
from datetime import datetime
from rich.console import Console
import uuid
try:
    import requests
except Exception:
    requests = None
import json
import urllib.request
import urllib.error

# DB drivers (import lazily if missing)
try:
    import mysql.connector
except Exception:
    mysql = None
try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None
try:
    from bson.objectid import ObjectId
except Exception:
    ObjectId = None
try:
    from cassandra.cluster import Cluster
except Exception:
    Cluster = None
try:
    import redis
except Exception:
    redis = None
try:
    from neo4j import GraphDatabase
except Exception:
    GraphDatabase = None

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


GEN_SLEEP = 5
GEN_INTERVAL = 6
SEED_CLIENTS = 10
SEED_PRODUCTS = 8
SEED_SUCURSALES = 5


def safe_exec(cursor, sql, params=None):
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
    except Exception as e:
        console.print(f"[yellow]Warning SQL:[/yellow] {e}")


def seed_mysql_core():
    """Inserta datos base en MySQL (Clientes, Productos, Sucursales, Stock) si faltan."""
    conn = cli_v2.mysql_conn
    if conn is None:
        console.print('[red]MySQL no inicializado, saltando seed MySQL[/red]')
        return
    cur = conn.cursor()

    # Clientes
    cur.execute('SELECT COUNT(*) FROM Cliente')
    cnt = cur.fetchone()[0]
    if cnt < SEED_CLIENTS:
        console.print(f'[dim]Insertando {SEED_CLIENTS - cnt} clientes de prueba...[/dim]')
        first_names = ['Ana','Juan','María','Luis','Sofía','Carlos','Lucía','Pedro','Marta','Diego','Laura','Javier']
        last_names = ['García','Pérez','Rodríguez','Gómez','Fernández','López','Martínez','Sánchez','Romero','Torres']
        for i in range(cnt + 1, SEED_CLIENTS + 1):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            name = f"{fn} {ln}"
            email = f'{fn.lower()}.{ln.lower()}{i}@example.com'
            safe_exec(cur, "INSERT IGNORE INTO Cliente (nombre, email, pais, telefono, domicilio, saldo, stars_acumuladas, fechaRegistro, estadoMembresia) VALUES (%s,%s,%s,%s,%s,0.0,0,CURDATE(),'Activo')", (name, email, 'Argentina', '0000', 'Domicilio',))
        conn.commit()

    # Productos
    cur.execute('SELECT COUNT(*) FROM Producto')
    cntp = cur.fetchone()[0]
    default_products = [('Latte','Bebida Caliente',4.5),('Espresso','Bebida Caliente',2.0),('Muffin','Panadería',3.0),('Bagel','Panadería',3.0),('Tea','Bebida Caliente',2.0),('Cookie','Snack',1.5),('Frappuccino','Bebida Fria',5.5),('Sandwich','Desayuno',6.0)]
    if cntp < SEED_PRODUCTS:
        console.print(f'[dim]Insertando productos de prueba...[/dim]')
        for name,tipo,precio in default_products[:SEED_PRODUCTS]:
            safe_exec(cur, "INSERT IGNORE INTO Producto (nombre, tipo, precio) VALUES (%s,%s,%s)", (name,tipo,precio))
        conn.commit()

    # Sucursales
    cur.execute('SELECT COUNT(*) FROM Sucursal')
    cnts = cur.fetchone()[0]
    if cnts < SEED_SUCURSALES:
        console.print(f'[dim]Insertando sucursales de prueba...[/dim]')
        for i in range(cnts + 1, SEED_SUCURSALES + 1):
            safe_exec(cur, "INSERT IGNORE INTO Sucursal (pais, ciudad, direccion, horario, capacidad) VALUES (%s,%s,%s,%s,%s)", ('Argentina', f'Ciudad_{i}', f'Calle {i}', '8-20', 30))
        conn.commit()

    # Stock simple: asignar cantidades
    cur.execute('SELECT id FROM Sucursal LIMIT 1')
    one_sucursal = cur.fetchone()
    cur.execute('SELECT id FROM Producto LIMIT 1')
    one_prod = cur.fetchone()
    if one_sucursal and one_prod:
        try:
            safe_exec(cur, "INSERT IGNORE INTO Stock (idSucursal, idProducto, cantidad) VALUES (%s,%s,%s)", (one_sucursal[0], one_prod[0], 100))
            conn.commit()
        except Exception:
            pass

    cur.close()


def pick_random_mysql_id(table_name):
    conn = cli_v2.mysql_conn
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT id FROM {table_name} ORDER BY RAND() LIMIT 1")
        r = cur.fetchone()
        return r[0] if r else None
    except Exception:
        return None
    finally:
        cur.close()


def fetch_all_clients():
    conn = cli_v2.mysql_conn
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        cur.execute('SELECT id, nombre, email FROM Cliente')
        return [{'id': r[0], 'nombre': r[1], 'email': r[2]} for r in cur.fetchall()]
    except Exception:
        return []
    finally:
        cur.close()


def fetch_all_sucursales():
    conn = cli_v2.mysql_conn
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        cur.execute('SELECT id, pais, ciudad, direccion FROM Sucursal')
        return [{'id': r[0], 'pais': r[1], 'ciudad': r[2], 'direccion': r[3]} for r in cur.fetchall()]
    except Exception:
        return []
    finally:
        cur.close()


def fetch_products_for_sucursal(sucursal_id):
    """Return list of products available in a sucursal with price and stock: [{'id','nombre','precio','cantidad'}]"""
    conn = cli_v2.mysql_conn
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        cur.execute('''
            SELECT p.id, p.nombre, p.precio, s.cantidad
            FROM Producto p
            JOIN Stock s ON p.id = s.idProducto
            WHERE s.idSucursal = %s AND s.cantidad > 0
        ''', (sucursal_id,))
        return [{'id': r[0], 'nombre': r[1], 'precio': float(r[2]), 'cantidad': r[3]} for r in cur.fetchall()]
    except Exception:
        # Fallback: return any product
        try:
            cur.execute('SELECT id, nombre, precio FROM Producto')
            return [{'id': r[0], 'nombre': r[1], 'precio': float(r[2]), 'cantidad': 999} for r in cur.fetchall()]
        except Exception:
            return []
    finally:
        cur.close()


def fetch_any_products():
    """Return products from Producto table as fallback: [{'id','nombre','precio','cantidad'}]"""
    conn = cli_v2.mysql_conn
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        cur.execute('SELECT id, nombre, precio FROM Producto')
        return [{'id': r[0], 'nombre': r[1], 'precio': float(r[2]), 'cantidad': 999} for r in cur.fetchall()]
    except Exception:
        return []
    finally:
        cur.close()



def generate_full_dummy():
    """Genera una orden completa y consistente usando los clientes/productos/sucursales de MySQL y sincroniza con Mongo/Cassandra/Neo4j/Redis."""
    # Primero intentar obtener un pedido desde el seed_service si está disponible
    def post_json(url, data=None, timeout=1.5):
        # Try requests if available, otherwise use urllib
        if requests is not None:
            return requests.post(url, json=data, timeout=timeout)
        # urllib implementation returns a SimpleNamespace-like object with status_code and json()
        req = urllib.request.Request(url, method='POST')
        body = b''
        if data is not None:
            body = json.dumps(data).encode('utf-8')
            req.add_header('Content-Type', 'application/json')
        try:
            with urllib.request.urlopen(req, data=body, timeout=timeout) as r:
                class R:
                    pass
                resp = R()
                resp.status_code = r.getcode()
                resp._body = r.read()
                def _json():
                    return json.loads(resp._body.decode('utf-8'))
                resp.json = _json
                return resp
        except urllib.error.URLError:
            raise

    try:
        resp = post_json('http://seed-service:8000/generate-order', timeout=1.5)
        if getattr(resp, 'status_code', None) == 200:
            order = resp.json()
            # convertir fecha ISO a datetime
            try:
                fecha = datetime.fromisoformat(order.get('fecha').replace('Z', '+00:00'))
            except Exception:
                fecha = datetime.utcnow()

            ticket_id = str(order.get('ticket_id'))
            ticket_num = int(order.get('ticket_id')) if order.get('ticket_id') is not None else None

            cliente_id = order.get('cliente_id')
            sucursal_id = order.get('sucursal_id')
            total = order.get('total')
            items = order.get('detalles', [])
            metodo_pago = order.get('metodo_pago')
            promocion_id = order.get('promocion_id')

            # Insertar en Mongo/Cassandra/MySQL stock/Neo4j/Redis usando la estructura ya existente
            # Mongo
            try:
                if getattr(cli_v2, 'mongo_client', None):
                    db = cli_v2.mongo_client.starbucks_transactions
                    mongo_doc = {
                        '_id': ObjectId() if ObjectId is not None else None,
                        'ticket_id': int(ticket_num) if ticket_num is not None else None,
                        'sucursal_id': sucursal_id,
                        'cliente_id': cliente_id,
                        'fecha': fecha,
                        'total': total,
                        'metodo_pago': metodo_pago,
                        'promocion_id': promocion_id,
                        'detalles': items
                    }
                    if mongo_doc['_id'] is not None:
                        db.ticket.insert_one(mongo_doc)
                    else:
                        mongo_doc.pop('_id', None)
                        db.ticket.insert_one(mongo_doc)
            except Exception as e:
                console.print(f'[red]Mongo insert error (seed_service):[/red] {e}')

            # Cassandra
            try:
                if getattr(cli_v2, 'cassandra_cluster', None):
                    session = cli_v2.cassandra_cluster.connect()
                    try:
                        cql = "INSERT INTO starbucks_analytics.historialcompra (idSucursal, fecha, ticket_num) VALUES (%s, %s, %s)"
                        with cli_v2.cassandra_lock:
                            fut = session.execute_async(cql, (sucursal_id, fecha, ticket_num))
                            fut.result()
                    finally:
                        try:
                            session.shutdown()
                        except Exception:
                            pass
            except Exception as e:
                console.print(f'[red]Cassandra insert error (seed_service):[/red] {e}')

            # MySQL stock update
            try:
                conn = cli_v2.mysql_conn
                if conn:
                    cur2 = conn.cursor()
                    for it in items:
                        pid = it.get('product_id')
                        qty = it.get('cantidad', 1)
                        if pid is not None:
                            cur2.execute('UPDATE Stock SET cantidad = GREATEST(0, cantidad - %s) WHERE idSucursal = %s AND idProducto = %s', (qty, sucursal_id, pid))
                    conn.commit()
                    cur2.close()
            except Exception as e:
                console.print(f'[red]MySQL stock update error (seed_service):[/red] {e}')

            # Neo4j
            try:
                if getattr(cli_v2, 'neo4j_driver', None):
                    with cli_v2.neo4j_driver.session() as s:
                        s.run("MERGE (c:Cliente {id: $id}) SET c.last_seen = $ts, c.name = coalesce(c.name, $name)", id=cliente_id, ts=fecha.isoformat(), name=f'Cliente {cliente_id}')
            except Exception as e:
                console.print(f'[red]Neo4j insert error (seed_service):[/red] {e}')

            # Redis
            try:
                if getattr(cli_v2, 'redis_client', None):
                    cli_v2.redis_client.set(f'last_ticket:sucursal:{sucursal_id}', ticket_id)
                    cli_v2.redis_client.incr('counter:tickets')
            except Exception as e:
                console.print(f'[red]Redis error (seed_service):[/red] {e}')

            return
    except Exception:
        # Seed service not available or failed; continuar con generador local
        pass
    try:
        # Leer clientes y sucursales reales
        clients = fetch_all_clients()
        sucursales = fetch_all_sucursales()
        if not clients or not sucursales:
            # Fallback a ids aleatorios si no hay datos
            cliente_id = pick_random_mysql_id('Cliente') or random.randint(1,500)
            sucursal_id = pick_random_mysql_id('Sucursal') or random.randint(1,10)
        else:
            cliente = random.choice(clients)
            cliente_id = cliente['id']
            sucursal = random.choice(sucursales)
            sucursal_id = sucursal['id']

        # Productos disponibles en esa sucursal
        available = fetch_products_for_sucursal(sucursal_id)
        if not available:
            # fallback: any product desde la tabla Producto
            available = fetch_any_products()

        # Elegir 1..3 items, con cantidades basadas en stock
        items = []
        if available:
            pool = available.copy()
            num_items = min(len(pool), random.randint(1,3))
            for _ in range(num_items):
                p = random.choice(pool)
                qty = 1
                if p.get('cantidad') and p['cantidad'] > 1:
                    qty = random.randint(1, min(3, p['cantidad']))
                # asegurar que id no sea None
                pid = p.get('id')
                if pid is None:
                    # intentar obtener any product id
                    anyp = fetch_any_products()
                    pid = anyp[0]['id'] if anyp else None
                items.append({'id': pid, 'nombre': p['nombre'], 'precio': p['precio'], 'cantidad': qty})
                # evitar repetir el mismo producto
                pool = [x for x in pool if x['id'] != p['id']]
        else:
            # generar mínimo 1 producto sintético
            items = [{'id': None, 'nombre': 'Producto_sintetico', 'precio': 3.0, 'cantidad': 1}]

        total = round(sum([it['precio'] * it['cantidad'] for it in items]), 2)
        fecha = datetime.utcnow()

        # Generar ticket_num/ticket_id: preferir Redis INCR para secuencia global
        ticket_num = None
        try:
            if getattr(cli_v2, 'redis_client', None):
                ticket_num = int(cli_v2.redis_client.incr('ticket_seq'))
        except Exception:
            ticket_num = None

        if ticket_num is None:
            # fallback local sequence using timestamp
            ticket_num = int(time.time() * 1000)

        ticket_id = str(ticket_num)

        # Mongo (documento con formato requerido)
        try:
            if getattr(cli_v2, 'mongo_client', None):
                db = cli_v2.mongo_client.starbucks_transactions
                # preparar detalles: list of {product_id, cantidad, precio}
                detalles = []
                for it in items:
                    detalles.append({
                        'product_id': it.get('id'),
                        'cantidad': it.get('cantidad', 1),
                        'precio': round(it.get('precio', 0) * it.get('cantidad', 1), 2)
                    })

                # intentar obtener promocion disponible (si existe)
                promocion_id = None
                try:
                    conn = cli_v2.mysql_conn
                    if conn:
                        curp = conn.cursor()
                        curp.execute('SELECT id FROM Promocion ORDER BY RAND() LIMIT 1')
                        rp = curp.fetchone()
                        if rp:
                            promocion_id = int(rp[0])
                        curp.close()
                except Exception:
                    promocion_id = None

                metodo_pago = random.choice(['Efectivo', 'Tarjeta', 'MercadoPago'])

                # _id must be an ObjectId; ticket_id is the numeric sequence
                mongo_id = ObjectId() if ObjectId is not None else None
                mongo_doc = {
                    '_id': mongo_id,
                    'ticket_id': int(ticket_num) if ticket_num is not None else None,
                    'sucursal_id': sucursal_id,
                    'cliente_id': cliente_id,
                    'fecha': fecha,
                    'total': total,
                    'metodo_pago': metodo_pago,
                    'promocion_id': promocion_id,
                    'detalles': detalles
                }

                # Insertar
                if mongo_id is not None:
                    db.ticket.insert_one(mongo_doc)
                else:
                    # Si no hay ObjectId disponible, dejar que Mongo genere _id pero mantener formato
                    mongo_doc.pop('_id', None)
                    db.ticket.insert_one(mongo_doc)
        except Exception as e:
            console.print(f'[red]Mongo insert error:[/red] {e}')

        # Cassandra
        try:
            if getattr(cli_v2, 'cassandra_cluster', None):
                session = cli_v2.cassandra_cluster.connect()
                try:
                    cql = "INSERT INTO starbucks_analytics.historialcompra (idSucursal, fecha, ticket_num) VALUES (%s, %s, %s)"
                    with cli_v2.cassandra_lock:
                        fut = session.execute_async(cql, (sucursal_id, fecha, ticket_num))
                        fut.result()
                finally:
                    try:
                        session.shutdown()
                    except Exception:
                        pass
        except Exception as e:
            console.print(f'[red]Cassandra insert error:[/red] {e}')

        # MySQL: actualizar sólo el stock (NO crear ni insertar tabla Ordenes en SQL)
        try:
            conn = cli_v2.mysql_conn
            if conn:
                try:
                    cur2 = conn.cursor()
                    for it in items:
                        if it.get('id'):
                            cur2.execute('UPDATE Stock SET cantidad = GREATEST(0, cantidad - %s) WHERE idSucursal = %s AND idProducto = %s', (it['cantidad'], sucursal_id, it['id']))
                    conn.commit()
                    cur2.close()
                except Exception:
                    pass
        except Exception as e:
            console.print(f'[red]MySQL stock update error:[/red] {e}')

        # Neo4j
        try:
            if getattr(cli_v2, 'neo4j_driver', None):
                with cli_v2.neo4j_driver.session() as s:
                    s.run("MERGE (c:Cliente {id: $id}) SET c.last_seen = $ts, c.name = coalesce(c.name, $name)", id=cliente_id, ts=fecha.isoformat(), name=f'Cliente {cliente_id}')
        except Exception as e:
            console.print(f'[red]Neo4j insert error:[/red] {e}')

        # Redis
        try:
            if getattr(cli_v2, 'redis_client', None):
                cli_v2.redis_client.set(f'last_ticket:sucursal:{sucursal_id}', ticket_id)
                cli_v2.redis_client.incr('counter:tickets')
        except Exception as e:
            console.print(f'[red]Redis error:[/red] {e}')




    except Exception:
        console.print(f"[red]Error en generate_full_dummy:\n{traceback.format_exc()}[/red]")


def generator_loop_full():
    # Esperar a que los clientes DB estén listos
    try:
        # Preferir init del propio cli_v2 si existe, sino inicializar locales
        if hasattr(cli_v2, 'init_db_clients'):
            try:
                cli_v2.init_db_clients()
            except Exception:
                init_db_clients()
        else:
            init_db_clients()
    except Exception as e:
        console.print(f"[red]No se pudieron inicializar clientes DB en cli_v3: {e}[/red]")
        return

    # Seed inicial de MySQL
    seed_mysql_core()

    # ráfaga inicial
    for _ in range(5):
        generate_full_dummy()
        time.sleep(0.3)

    while True:
        try:
            generate_full_dummy()
        except Exception as e:
            console.print(f"[red]Error en generador completo: {e}[/red]")
        time.sleep(GEN_INTERVAL)


def start_background_full_generator():
    t = threading.Thread(target=generator_loop_full, daemon=True)
    t.start()


def init_db_clients():
    """Inicializa clientes DB y los pone sobre el módulo cli_v2 para compatibilidad."""
    # MySQL
    try:
        conn = None
        if mysql is not None:
            conn = mysql.connector.connect(host='mysql', user='root', password='root_password', database='my_data_warehouse')
        cli_v2.mysql_conn = conn
    except Exception as e:
        console.print(f"[yellow]No se pudo conectar a MySQL: {e}[/yellow]")
        cli_v2.mysql_conn = None

    # Mongo
    try:
        mc = None
        if MongoClient is not None:
            mc = MongoClient('mongodb://rootuser:rootpassword@mongodb:27017/', serverSelectionTimeoutMS=2000)
        cli_v2.mongo_client = mc
    except Exception as e:
        console.print(f"[yellow]No se pudo conectar a Mongo: {e}[/yellow]")
        cli_v2.mongo_client = None

    # Cassandra
    try:
        cc = None
        if Cluster is not None:
            cc = Cluster(['cassandra'])
        cli_v2.cassandra_cluster = cc
    except Exception as e:
        console.print(f"[yellow]No se pudo conectar a Cassandra: {e}[/yellow]")
        cli_v2.cassandra_cluster = None

    # Redis
    try:
        rc = None
        if redis is not None:
            rc = redis.Redis(host='redis', port=6379, db=0, socket_connect_timeout=2)
        cli_v2.redis_client = rc
    except Exception as e:
        console.print(f"[yellow]No se pudo conectar a Redis: {e}[/yellow]")
        cli_v2.redis_client = None

    # Neo4j
    try:
        ng = None
        if GraphDatabase is not None:
            ng = GraphDatabase.driver('bolt://neo4j:7687', auth=('neo4j', 'neo4jpassword'))
        cli_v2.neo4j_driver = ng
    except Exception as e:
        console.print(f"[yellow]No se pudo conectar a Neo4j: {e}[/yellow]")
        cli_v2.neo4j_driver = None

    # misc
    cli_v2.uuid = uuid
    cli_v2.cassandra_lock = threading.Lock()



def run():
    # Iniciar generador silencioso en background y luego delegar la TUI de cli_v2
    try:
        start_background_full_generator()
    except Exception as e:
        console.print(f"[yellow]No se pudo iniciar generador full: {e}[/yellow]")

    # Ejecutar la TUI original (usa run_tui de cli_v2)
    try:
        cli_v2.run_tui()
    except Exception as e:
        console.print(f"[red]Error launching TUI from cli_v2: {e}\n{traceback.format_exc()}[/red]")


if __name__ == '__main__':
    run()
