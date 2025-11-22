from fastapi import FastAPI
from pydantic import BaseModel
import random
import time
import os
import mysql.connector
import redis

app = FastAPI(title="Seed Service")


class GenerateRequest(BaseModel):
    # optional, allow caller to constrain choices
    cliente_id: int | None = None
    sucursal_id: int | None = None


def get_mysql_conn():
    return mysql.connector.connect(host=os.environ.get('MYSQL_HOST','mysql'),
                                   user=os.environ.get('MYSQL_USER','root'),
                                   password=os.environ.get('MYSQL_PASS','root_password'),
                                   database=os.environ.get('MYSQL_DB','my_data_warehouse'))


def get_redis_conn():
    try:
        return redis.Redis(host=os.environ.get('REDIS_HOST','redis'), port=int(os.environ.get('REDIS_PORT',6379)), db=0, socket_connect_timeout=2)
    except Exception:
        return None


@app.post('/generate-order')
def generate_order(req: GenerateRequest | None = None):
    # Build an order JSON using MySQL data; guarantee product_id not null
    conn = None
    try:
        conn = get_mysql_conn()
        cur = conn.cursor()

        rconn = get_redis_conn()
        ticket_id = None
        if rconn:
            try:
                ticket_id = int(rconn.incr('ticket_seq'))
            except Exception:
                ticket_id = None

        # clientes
        if req and req.cliente_id:
            cliente_id = req.cliente_id
        else:
            cur.execute('SELECT id FROM Cliente')
            rows = cur.fetchall()
            cliente_id = random.choice([r[0] for r in rows]) if rows else None

        # sucursal
        if req and req.sucursal_id:
            sucursal_id = req.sucursal_id
        else:
            cur.execute('SELECT id FROM Sucursal')
            rows = cur.fetchall()
            sucursal_id = random.choice([r[0] for r in rows]) if rows else None

        # productos disponibles en la sucursal
        productos = []
        if sucursal_id is not None:
            cur.execute('''
                SELECT p.id, p.nombre, p.precio, s.cantidad
                FROM Producto p
                JOIN Stock s ON p.id = s.idProducto
                WHERE s.idSucursal = %s AND s.cantidad > 0
            ''', (sucursal_id,))
            productos = [{'id': r[0], 'nombre': r[1], 'precio': float(r[2]), 'cantidad': r[3]} for r in cur.fetchall()]

        # fallback a cualquier producto
        if not productos:
            cur.execute('SELECT id, nombre, precio FROM Producto')
            productos = [{'id': r[0], 'nombre': r[1], 'precio': float(r[2]), 'cantidad': 999} for r in cur.fetchall()]

        # elegir 1..3 items
        items = []
        if productos:
            pool = productos.copy()
            num_items = min(len(pool), random.randint(1,3))
            for _ in range(num_items):
                p = random.choice(pool)
                qty = 1
                if p.get('cantidad') and p['cantidad'] > 1:
                    qty = random.randint(1, min(3, p['cantidad']))
                items.append({'product_id': int(p['id']), 'cantidad': int(qty), 'precio': round(p['precio'] * qty, 2)})
                pool = [x for x in pool if x['id'] != p['id']]

        # total
        total = round(sum([it['precio'] for it in items]), 2)

        # promocion random
        promocion_id = None
        try:
            cur.execute('SELECT id FROM Promocion')
            pr = cur.fetchall()
            if pr:
                promocion_id = int(random.choice(pr)[0])
        except Exception:
            promocion_id = None

        metodo_pago = random.choice(['Efectivo','Tarjeta','MercadoPago'])

        # If ticket_id not obtained via Redis, fallback to timestamp-based.
        if ticket_id is None:
            ticket_id = int(time.time() * 1000)
        fecha = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

        return {
            'ticket_id': ticket_id,
            'sucursal_id': int(sucursal_id) if sucursal_id is not None else None,
            'cliente_id': int(cliente_id) if cliente_id is not None else None,
            'fecha': fecha,
            'total': total,
            'metodo_pago': metodo_pago,
            'promocion_id': promocion_id,
            'detalles': items
        }

    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
