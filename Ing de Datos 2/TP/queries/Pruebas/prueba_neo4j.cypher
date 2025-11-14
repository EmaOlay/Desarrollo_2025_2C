CALL dbms.components() YIELD name, versions
WHERE name = 'Neo4j Kernel'
RETURN 'Conexión Exitosa a Neo4j' AS Status, versions[0] AS Version;

MATCH (n) RETURN count(n) AS TotalNodes;

MATCH (p:Producto)<-[:COMPRA]-(c:Cliente)
RETURN p.nombre AS Producto, COUNT(DISTINCT c) AS NumeroDeClientes
ORDER BY NumeroDeClientes DESC
LIMIT 5;