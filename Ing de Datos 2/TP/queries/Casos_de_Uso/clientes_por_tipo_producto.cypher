MATCH (c:Cliente)-[:COMPRA]->(p:Producto)
WITH c, COLLECT(DISTINCT p.tipo) AS tipos_productos_comprados
WHERE size(tipos_productos_comprados) >= 3
RETURN c.nombre AS Cliente, tipos_productos_comprados, size(tipos_productos_comprados) AS Cantidad_Tipos_Distintos
ORDER BY Cantidad_Tipos_Distintos DESC, Cliente ASC
// Clientes que compraron ≥3 tipos de producto distintos