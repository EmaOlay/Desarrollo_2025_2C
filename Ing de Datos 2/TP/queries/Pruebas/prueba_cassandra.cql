-- Script de prueba para verificar la conectividad a Cassandra y consultar datos.

-- 1. Mostrar la versión del servidor
SELECT
    release_version AS Version,
    cluster_name AS Cluster
FROM
    system.local;

-- 2. Mostrar Keyspaces (equivalente a SHOW DATABASES en SQL)
DESCRIBE KEYSPACES;

-- 3. Usar el keyspace de la aplicación
USE starbucks_analytics;

-- 4. Describir la tabla para verificar el esquema
DESCRIBE TABLE HistorialCompra;

-- 5. Consultar todos los datos de la tabla
SELECT 'Tabla HistorialCompra' AS '';
SELECT * FROM HistorialCompra;