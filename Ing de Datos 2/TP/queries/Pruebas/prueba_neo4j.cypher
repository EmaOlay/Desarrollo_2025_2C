// Script de prueba para verificar la conectividad a Neo4j y la versión del grafo.

// 1. Mostrar la versión del servidor (implícitamente prueba la conexión)
CALL dbms.components() YIELD name, versions
WHERE name = 'Neo4j Kernel'
RETURN 'Conexión Exitosa a Neo4j' AS Status, versions[0] AS Version;

// 2. Mostrar la información de un nodo simple (opcional, si tienes datos iniciales)
// Si ya has cargado datos, esto asegura que el query engine está funcionando.
// Si no tienes datos, puedes omitir esta parte.
// MATCH (n) RETURN count(n) AS TotalNodes;