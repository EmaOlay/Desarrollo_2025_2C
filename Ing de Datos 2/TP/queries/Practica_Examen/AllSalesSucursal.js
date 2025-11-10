print("\n\nTodos los tickets de las sucus 2 y 3\n\n");
print(db.ticket.find(
    {
        total:{$gte:32}
        // $or:[
        //     {ticket_id: 1},
        //     {sucursal_id: 3}
        // ] 
            // sucursal_id: { $in: [2,3] },
            // ticket_id: 1
    },

)
);
// print("\n\nQuery de total vendido por sucursales 2,3 agregado")
// print(
// db.ticket.aggregate([
//     // 1. Filtrar los tickets por la lista de IDs de sucursal
//     {
//         $match: {
//             sucursal_id: { $in: [2,3] }
//         }
//     },
//     // 2. Desestructurar el array 'detalles' para tener un documento por producto vendido
//     {
//         $unwind: "$detalles"
//     },
//     // 3. Agrupar por idProducto y sumar la cantidad vendida
//     {
//         $group: {
//             _id: "$detalles.product_id",
//             totalVendido: { $sum: "$detalles.cantidad" }
//         }
//     },
//     // 4. Ordenar por la cantidad vendida (descendente)
//     {
//         $sort: { totalVendido: -1 }
//     },
//     // 5. Limitar a los 5 principales
//     {
//         $limit: 5
//     },
//     // 6. Proyectar el resultado final
//     {
//         $project: {
//             _id: 0,
//             idProducto: "$_id",
//             totalVendido: 1
//         }
//     }
// ]).forEach(printjson)
// );