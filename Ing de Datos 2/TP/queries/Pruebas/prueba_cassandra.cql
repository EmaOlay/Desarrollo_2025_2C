-- Script de prueba para verificar la conectividad a Cassandra y listar keyspaces.

-- 1. Mostrar estado de conexión (esto se hace implícitamente al conectar)
-- 2. Mostrar la versión del servidor
SELECT
    release_version AS Version,
    cluster_name AS Cluster
FROM
    system.local;

-- 3. Mostrar Keyspaces (equivalente a SHOW DATABASES en SQL)
DESCRIBE KEYSPACES;
