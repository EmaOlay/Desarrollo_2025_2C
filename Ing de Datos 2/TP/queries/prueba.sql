-- Prueba simple para verificar la conectividad de la TUI a MySQL

SELECT 
    'Conexión Exitosa a MySQL' AS Status, 
    VERSION() AS Version, 
    CURRENT_USER() AS User;
    