SELECT t1.*
FROM Producto t1
INNER JOIN Tipo_Producto t2 ON t1.tipo = t2.idTipoProducto 
WHERE t1.precio > 5
AND lower(t1.tipo) LIKE 'bebida'