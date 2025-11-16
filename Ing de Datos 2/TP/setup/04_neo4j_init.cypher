// setup/04_neo4j_init.cypher

// 1. Limpiar la base de datos
MATCH (n) DETACH DELETE n;

// 2. Crear Nodos de Clientes
CREATE (c1:Cliente {id: 1, nombre: 'Alice Johnson', email: 'alice@example.com'});
CREATE (c2:Cliente {id: 2, nombre: 'Jhon Doe', email: 'john.doe@example.com'});
CREATE (c3:Cliente {id: 101, nombre: 'Ana García', email: 'ana.garcia@example.com'});
CREATE (c4:Cliente {id: 102, nombre: 'Juan Perez', email: 'juan.perez@email.com'});
CREATE (c5:Cliente {id: 103, nombre: 'Carlos Sanchez', email: 'carlos.sanchez@example.com'});

// 3. Crear Nodos de Productos
CREATE (p1:Producto {id: 1, nombre: 'Latte', precio: 4.50, tipo: 'Bebida Caliente'});
CREATE (p2:Producto {id: 2, nombre: 'Muffin', precio: 3.00, tipo: 'Panadería/Pasteleria'});
CREATE (p3:Producto {id: 3, nombre: 'Frappuccino', precio: 5.50, tipo: 'Bebida Fria'});

// 4. Crear Nodos de Sucursales
CREATE (s1:Sucursal {id: 1, nombre: 'Sucursal New York', ciudad: 'New York'});
CREATE (s2:Sucursal {id: 2, nombre: 'Sucursal Buenos Aires Centro', ciudad: 'Buenos Aires'});
CREATE (s3:Sucursal {id: 3, nombre: 'Sucursal Buenos Aires Libertador', ciudad: 'Buenos Aires'});
CREATE (s4:Sucursal {id: 101, nombre: 'Sucursal Cordoba', ciudad: 'Cordoba'});
CREATE (s5:Sucursal {id: 102, nombre: 'Sucursal Rosario', ciudad: 'Rosario'});


// 5. Crear Relaciones de Compra (Cliente)-[:COMPRA]->(Producto) y (Compra)-[:EN]->(Sucursal)

// Ticket 1
MATCH (c:Cliente {id: 1}), (p:Producto {id: 1}), (s:Sucursal {id: 2})
CREATE (c)-[:COMPRA {ticket_id: 1, cantidad: 2, fecha: datetime('2024-09-01T08:30:00Z')}]->(p);

// Ticket 2
MATCH (c:Cliente {id: 2}), (p:Producto {id: 2}), (s:Sucursal {id: 102})
CREATE (c)-[:COMPRA {ticket_id: 2, cantidad: 1, fecha: datetime('2025-09-01T08:30:00Z')}]->(p);

// Ticket 3
MATCH (c:Cliente {id: 1}), (p1:Producto {id: 1}), (p2:Producto {id: 2}), (p3:Producto {id: 3}), (s:Sucursal {id: 3})
CREATE (c)-[:COMPRA {ticket_id: 3, cantidad: 2, fecha: datetime('2025-09-01T09:00:00Z')}]->(p1),
       (c)-[:COMPRA {ticket_id: 3, cantidad: 1, fecha: datetime('2025-09-01T09:00:00Z')}]->(p2),
       (c)-[:COMPRA {ticket_id: 3, cantidad: 1, fecha: datetime('2025-09-01T09:00:00Z')}]->(p3);

// Ticket 4
MATCH (c:Cliente {id: 2}), (p:Producto {id: 3}), (s:Sucursal {id: 101})
CREATE (c)-[:COMPRA {ticket_id: 4, cantidad: 2, fecha: datetime('2025-09-02T15:00:00Z')}]->(p);

// Ticket 57
MATCH (c:Cliente {id: 1}), (p1:Producto {id: 3}), (p2:Producto {id: 2}), (s:Sucursal {id: 3})
CREATE (c)-[:COMPRA {ticket_id: 57, cantidad: 2, fecha: datetime('2025-09-01T15:00:00Z')}]->(p1),
       (c)-[:COMPRA {ticket_id: 57, cantidad: 1, fecha: datetime('2025-09-01T15:00:00Z')}]->(p2);

// Nuevas compras para hacer el grafo más interesante
MATCH (c103:Cliente {id: 103}), (p1:Producto {id: 1})
CREATE (c103)-[:COMPRA {ticket_id: 1001, cantidad: 1, fecha: datetime('2025-10-10T10:00:00Z')}]->(p1);

MATCH (c101:Cliente {id: 101}), (p2:Producto {id: 2})
CREATE (c101)-[:COMPRA {ticket_id: 1002, cantidad: 1, fecha: datetime('2025-10-11T11:00:00Z')}]->(p2);

MATCH (c102:Cliente {id: 102}), (p3:Producto {id: 3})
CREATE (c102)-[:COMPRA {ticket_id: 1003, cantidad: 1, fecha: datetime('2025-10-12T12:00:00Z')}]->(p3);

MATCH (c1:Cliente {id: 1}), (p3:Producto {id: 3})
CREATE (c1)-[:COMPRA {ticket_id: 1004, cantidad: 1, fecha: datetime('2025-10-13T13:00:00Z')}]->(p3);

MATCH (c2:Cliente {id: 2}), (p1:Producto {id: 1})
CREATE (c2)-[:COMPRA {ticket_id: 1005, cantidad: 1, fecha: datetime('2025-10-14T14:00:00Z')}]->(p1);

MATCH (c101:Cliente {id: 101}), (p1:Producto {id: 1})
CREATE (c101)-[:COMPRA {ticket_id: 1006, cantidad: 1, fecha: datetime('2025-10-15T15:00:00Z')}]->(p1);
