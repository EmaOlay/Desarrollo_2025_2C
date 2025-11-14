// setup/04_neo4j_init.cypher

// 1. Limpiar la base de datos
MATCH (n) DETACH DELETE n;

// 2. Crear Nodos de Clientes
UNWIND range(1, 10) AS i
CREATE (c:Cliente {id: i, nombre: 'Cliente ' + i, email: 'cliente' + i + '@example.com'});

// 3. Crear Nodos de Productos
UNWIND range(1, 10) AS i
CREATE (p:Producto {id: i, nombre: 'Producto ' + i, precio: toFloat(rand() * 100 + 10)});

// 4. Crear Nodos de Sucursales
CREATE (s1:Sucursal {id: 1, nombre: 'Sucursal Centro', ciudad: 'Buenos Aires'});
CREATE (s2:Sucursal {id: 2, nombre: 'Sucursal Norte', ciudad: 'Buenos Aires'});
CREATE (s3:Sucursal {id: 3, nombre: 'Sucursal Sur', ciudad: 'Córdoba'});

// 5. Crear Relaciones de Compra (Cliente)-[:COMPRA]->(Producto)
// Aseguramos que algunos productos sean comprados por más clientes
// y que cada compra esté asociada a una sucursal.

// Cliente 1 compra varios productos
MATCH (c:Cliente {id: 1}), (p1:Producto {id: 1}), (p2:Producto {id: 2}), (p3:Producto {id: 3}), (s:Sucursal {id: 1})
CREATE (c)-[:COMPRA {cantidad: 2, fecha: datetime('2023-01-15T10:00:00')}]->(p1),
       (c)-[:COMPRA {cantidad: 1, fecha: datetime('2023-01-15T10:00:00')}]->(p2),
       (c)-[:COMPRA {cantidad: 3, fecha: datetime('2023-02-20T11:30:00')}]->(p3);

// Cliente 2 compra algunos productos, incluyendo uno ya comprado por Cliente 1
MATCH (c:Cliente {id: 2}), (p1:Producto {id: 1}), (p4:Producto {id: 4}), (s:Sucursal {id: 2})
CREATE (c)-[:COMPRA {cantidad: 1, fecha: datetime('2023-01-20T14:00:00')}]->(p1),
       (c)-[:COMPRA {cantidad: 2, fecha: datetime('2023-03-01T09:00:00')}]->(p4);

// Cliente 3 compra algunos productos, incluyendo uno ya comprado por Cliente 1 y 2
MATCH (c:Cliente {id: 3}), (p1:Producto {id: 1}), (p5:Producto {id: 5}), (s:Sucursal {id: 1})
CREATE (c)-[:COMPRA {cantidad: 1, fecha: datetime('2023-02-01T16:00:00')}]->(p1),
       (c)-[:COMPRA {cantidad: 1, fecha: datetime('2023-04-10T12:00:00')}]->(p5);

// Cliente 4 compra un producto
MATCH (c:Cliente {id: 4}), (p6:Producto {id: 6}), (s:Sucursal {id: 3})
CREATE (c)-[:COMPRA {cantidad: 1, fecha: datetime('2023-03-10T13:00:00')}]->(p6);

// Cliente 5 compra un producto
MATCH (c:Cliente {id: 5}), (p7:Producto {id: 7}), (s:Sucursal {id: 2})
CREATE (c)-[:COMPRA {cantidad: 1, fecha: datetime('2023-04-05T17:00:00')}]->(p7);

// Clientes restantes compran productos variados, algunos compartidos
MATCH (c:Cliente {id: 6}), (p:Producto {id: 2}), (s:Sucursal {id: 1})
CREATE (c)-[:COMPRA {cantidad: 1, fecha: datetime('2023-05-01T10:00:00')}]->(p);

MATCH (c:Cliente {id: 7}), (p:Producto {id: 3}), (s:Sucursal {id: 3})
CREATE (c)-[:COMPRA {cantidad: 1, fecha: datetime('2023-06-15T11:00:00')}]->(p);

MATCH (c:Cliente {id: 8}), (p:Producto {id: 8}), (s:Sucursal {id: 1})
CREATE (c)-[:COMPRA {cantidad: 1, fecha: datetime('2023-07-20T14:00:00')}]->(p);

MATCH (c:Cliente {id: 9}), (p:Producto {id: 9}), (s:Sucursal {id: 2})
CREATE (c)-[:COMPRA {cantidad: 1, fecha: datetime('2023-08-01T15:00:00')}]->(p);

MATCH (c:Cliente {id: 10}), (p:Producto {id: 10}), (s:Sucursal {id: 3})
CREATE (c)-[:COMPRA {cantidad: 1, fecha: datetime('2023-09-10T16:00:00')}]->(p);

// Relacionar las compras con las sucursales
// Esto se hace implícitamente en los CREATEs anteriores, pero si las relaciones
// COMPRA ya existieran, se podría hacer así:
// MATCH (c:Cliente)-[compra:COMPRA]->(p:Producto), (s:Sucursal)
// WHERE compra.fecha >= datetime('2023-01-01') AND compra.fecha <= datetime('2023-12-31')
// AND s.id = CASE
//     WHEN p.id IN [1,2,3,6,8] THEN 1 // Productos comprados en Sucursal 1
//     WHEN p.id IN [1,4,7,9] THEN 2 // Productos comprados en Sucursal 2
//     ELSE 3 // Productos comprados en Sucursal 3
// END
// CREATE (compra)-[:REALIZADA_EN]->(s);
