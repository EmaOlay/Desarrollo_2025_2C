// Este script espera que la variable 'sucursalIds' sea inyectada
// como un array de números, ej: sucursalIds = [1, 5, 8];

db.ticket.aggregate([
    // 1. Filtrar los tickets por la lista de IDs de sucursal
    {
        $match: {
            sucursal_id: { $in: sucursalIds }
        }
    },
    // 2. Desestructurar el array 'detalles' para tener un documento por producto vendido
    {
        $unwind: "$detalles"
    },
    // 3. Agrupar por idProducto y sumar la cantidad vendida
    {
        $group: {
            _id: "$detalles.producto_id",
            totalVendido: { $sum: "$detalles.cantidad" }
        }
    },
    // 4. Ordenar por la cantidad vendida (descendente)
    {
        $sort: { totalVendido: -1 }
    },
    // 5. Limitar a los 5 principales
    {
        $limit: 5
    },
    // 6. Proyectar el resultado final
    {
        $project: {
            _id: 0,
            idProducto: "$_id",
            totalVendido: 1
        }
    }
]).forEach(printjson);