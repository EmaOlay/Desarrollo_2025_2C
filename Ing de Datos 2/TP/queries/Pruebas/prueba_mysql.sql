-- Prueba completa para verificar la conectividad de la TUI a MySQL y consultar todas las tablas
SELECT 
    'Conexión Exitosa a MySQL' AS Status, 
    VERSION() AS Version, 
    CURRENT_USER() AS User;

-- Listar todas las tablas para confirmar que el esquema se creó correctamente
SHOW TABLES;

-- Consultar cada una de las tablas para verificar que los datos se insertaron
SELECT 'Tabla Cliente' AS '';
SELECT * FROM Cliente;

SELECT 'Tabla Sucursal' AS '';
SELECT * FROM Sucursal;

SELECT 'Tabla Producto' AS '';
SELECT * FROM Producto;

SELECT 'Tabla Promocion' AS '';
SELECT * FROM Promocion;

SELECT 'Tabla Stock' AS '';
SELECT * FROM Stock;

SELECT 'Tabla Tipo_Producto' AS '';
SELECT * FROM Tipo_Producto;