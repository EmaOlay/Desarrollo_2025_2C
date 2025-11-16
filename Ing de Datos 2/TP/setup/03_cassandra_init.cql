-- setup/03_cassandra_init.cql

-- ----------------------------------------------------
-- 1. KEYSPACE CREATION
-- We use SimpleStrategy as it's common for single-datacenter local setups
-- ----------------------------------------------------
CREATE KEYSPACE IF NOT EXISTS starbucks_analytics
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE starbucks_analytics;

DROP TABLE IF EXISTS HistorialCompra;


-- ----------------------------------------------------
-- 2. TABLE CREATION (HistorialCompra)
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS HistorialCompra (
    idSucursal int,
    fecha timestamp,
    ticket_num int,
    PRIMARY KEY (idSucursal, fecha)
) WITH CLUSTERING ORDER BY (fecha DESC);


-- ----------------------------------------------------
-- 3. INITIAL DATA INSERT
-- Example historical record
-- ----------------------------------------------------
INSERT INTO HistorialCompra (idSucursal, fecha, ticket_num)
VALUES (
    2, -- sucursal_id from MongoDB ticket_id: 1
    '2024-09-01 08:30:00+0000', -- fecha from MongoDB ticket_id: 1
    1 -- ticket_id from MongoDB ticket_id: 1
);

INSERT INTO HistorialCompra (idSucursal, fecha, ticket_num) VALUES (2, '2024-09-01 08:30:00+0000', 1);
INSERT INTO HistorialCompra (idSucursal, fecha, ticket_num) VALUES (102, '2025-09-01 08:30:00+0000', 2);
INSERT INTO HistorialCompra (idSucursal, fecha, ticket_num) VALUES (3, '2025-09-01 09:00:00+0000', 3);
INSERT INTO HistorialCompra (idSucursal, fecha, ticket_num) VALUES (101, '2025-09-02 15:00:00+0000', 4);
INSERT INTO HistorialCompra (idSucursal, fecha, ticket_num) VALUES (3, '2025-09-01 15:00:00+0000', 57);