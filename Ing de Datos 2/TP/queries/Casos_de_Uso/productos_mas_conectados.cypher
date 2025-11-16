MATCH (c:Cliente)-[:COMPRA]->(p:Producto)
WITH p, count(DISTINCT c) AS numero_de_clientes
RETURN p.nombre, numero_de_clientes
ORDER BY numero_de_clientes DESC
// Productos más conectados (comprados por mayor número de clientes)