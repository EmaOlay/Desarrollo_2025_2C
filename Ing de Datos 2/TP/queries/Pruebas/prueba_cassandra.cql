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

USE starbucks_analytics;

--
SELECT idSucursal, fecha, ticket_num
            FROM HistorialCompra
            WHERE idSucursal = 3
            AND fecha >= '2025-09-01 00:00:00+0000'
            AND fecha <= '2025-09-01 23:59:59+0000';

    
select * from historialcompra;