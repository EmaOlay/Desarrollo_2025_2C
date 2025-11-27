from fastapi import FastAPI
from pydantic import BaseModel
import random
import time
import os
import mysql.connector
import redis
import pymongo
import logging
from cassandra.cluster import Cluster
from neo4j import GraphDatabase
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def get_mongo_conn():
    try:
        client = pymongo.MongoClient(host=os.environ.get('MONGO_HOST', 'mongodb'),
                                     port=int(os.environ.get('MONGO_PORT', 27017)),
                                     username=os.environ.get('MONGO_USER', 'rootuser'),
                                     password=os.environ.get('MONGO_PASS', 'rootpassword'),
                                     authSource='admin')
        return client[os.environ.get('MONGO_DB', 'starbucks_transactions')]
    except Exception as e:
        logging.error(f"Could not connect to MongoDB: {e}")
        return None

def get_cassandra_conn():
    try:
        cluster = Cluster([os.environ.get('CASSANDRA_HOST', 'cassandra')])
        session = cluster.connect()
        return session
    except Exception as e:
        logging.error(f"Could not connect to Cassandra: {e}")
        return None

def get_neo4j_driver():
    try:
        driver = GraphDatabase.driver(f"bolt://{os.environ.get('NEO4J_HOST', 'neo4j')}:7687",
                                      auth=(os.environ.get('NEO4J_USER', 'neo4j'), os.environ.get('NEO4J_PASS', 'neo4jpassword')))
        return driver
    except Exception as e:
        logging.error(f"Could not connect to Neo4j: {e}")
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
                items.append({'product_id': int(p['id']), 'nombre': p['nombre'], 'cantidad': int(qty), 'precio': round(p['precio'] * qty, 2)})
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
        
        fecha_str = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        fecha_dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))


        order = {
            'ticket_id': ticket_id,
            'sucursal_id': int(sucursal_id) if sucursal_id is not None else None,
            'cliente_id': int(cliente_id) if cliente_id is not None else None,
            'fecha': fecha_str,
            'total': total,
            'metodo_pago': metodo_pago,
            'promocion_id': promocion_id,
            'detalles': items
        }

        # Insert into MongoDB
        mongo_db = get_mongo_conn()
        if mongo_db is not None:
            try:
                # MongoDB wants datetime objects for ISODate
                order_for_mongo = order.copy()
                order_for_mongo['fecha'] = fecha_dt
                result = mongo_db.ticket.insert_one(order_for_mongo)
                logging.info(f"Inserted order {result.inserted_id} into MongoDB.")
            except Exception as e:
                logging.error(f"Failed to insert order into MongoDB: {e}")

        # Insert into Cassandra
        cassandra_session = get_cassandra_conn()
        if cassandra_session is not None:
            try:
                cql = "INSERT INTO starbucks_analytics.historialcompra (idSucursal, fecha, ticket_num) VALUES (%s, %s, %s)"
                cassandra_session.execute(cql, (sucursal_id, fecha_dt, ticket_id))
                logging.info(f"Inserted order {ticket_id} into Cassandra.")
            except Exception as e:
                logging.error(f"Failed to insert order into Cassandra: {e}")
            finally:
                cassandra_session.cluster.shutdown()

        # Update MySQL Stock
        try:
            cur2 = conn.cursor()
            for it in items:
                pid = it.get('product_id')
                qty = it.get('cantidad', 1)
                if pid is not None:
                    cur2.execute('UPDATE Stock SET cantidad = GREATEST(0, cantidad - %s) WHERE idSucursal = %s AND idProducto = %s', (qty, sucursal_id, pid))
            conn.commit()
            logging.info(f"Updated stock in MySQL for ticket {ticket_id}.")
            cur2.close()
        except Exception as e:
            logging.error(f"Failed to update stock in MySQL: {e}")

        # Update Neo4j
        neo4j_driver = get_neo4j_driver()
        if neo4j_driver is not None:
            try:
                with neo4j_driver.session() as s:
                    # First, ensure the client exists
                    s.run("MERGE (c:Cliente {id: $id}) SET c.last_seen = $ts, c.name = coalesce(c.name, $name)", 
                          id=cliente_id, ts=fecha_str, name=f'Cliente {cliente_id}')
                    
                    # Then, create the purchase relationships for each product in the order
                    for item in items:
                        s.run("""
                            MERGE (c:Cliente {id: $cliente_id})
                            MERGE (p:Producto {id: $product_id})
                            ON CREATE SET p.nombre = $product_name
                            CREATE (c)-[:COMPRO {ticket_id: $ticket_id, fecha: $fecha, cantidad: $cantidad}]->(p)
                        """, {
                            "cliente_id": cliente_id,
                            "product_id": item['product_id'],
                            "product_name": item['nombre'],
                            "ticket_id": ticket_id,
                            "fecha": fecha_str,
                            "cantidad": item['cantidad']
                        })
                    logging.info(f"Created purchase relationships in Neo4j for ticket {ticket_id}.")
            except Exception as e:
                logging.error(f"Failed to update Neo4j: {e}")
            finally:
                neo4j_driver.close()

        # Update Redis
        if rconn is not None:
            try:
                rconn.set(f'last_ticket:sucursal:{sucursal_id}', ticket_id)
                rconn.incr('counter:tickets')
                logging.info(f"Updated Redis for ticket {ticket_id}.")
            except Exception as e:
                logging.error(f"Failed to update Redis: {e}")


        return order

    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

