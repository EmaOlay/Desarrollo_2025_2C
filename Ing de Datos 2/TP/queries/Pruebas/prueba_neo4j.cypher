-- Script de prueba para verificar la conectividad a Neo4j y consultar el grafo.

-- 1. Verificar la conexión y la versión
CALL dbms.components() YIELD name, versions
WHERE name = 'Neo4j Kernel'
RETURN 'Conexión Exitosa a Neo4j' AS Status, versions[0] AS Version;

-- 2. Contar todos los nodos y relaciones para tener una vista general
MATCH (n) RETURN 'Total de Nodos' AS Metrica, count(n) AS Valor
UNION ALL
MATCH ()-[r]->() RETURN 'Total de Relaciones' AS Metrica, count(r) AS Valor;

-- 3. Consultar una muestra de cada tipo de nodo
MATCH (c:Cliente)
RETURN c AS Nodo, 'Cliente' AS Tipo
LIMIT 5
UNION ALL
MATCH (p:Producto)
RETURN p AS Nodo, 'Producto' AS Tipo
LIMIT 5
UNION ALL
MATCH (s:Sucursal)
RETURN s AS Nodo, 'Sucursal' AS Tipo
LIMIT 5;

-- 4. Consultar una muestra de las relaciones de COMPRA
MATCH (c:Cliente)-[r:COMPRA]->(p:Producto)
RETURN c.nombre AS Cliente, type(r) AS Relacion, p.nombre AS Producto, r.fecha AS Fecha
LIMIT 10;