SELECT
    id,
    nombre,
    descuento,
    fechaInicio,
    fechaFin
FROM
    Promocion
WHERE
    CURDATE() BETWEEN fechaInicio AND fechaFin
ORDER BY
    descuento DESC;