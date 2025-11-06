// Script de prueba para verificar la conectividad y la base de datos 'starbucks_transactions'.

// 1. Mostrar estado de conexión y versión
print("--- Conexión y Estado ---");
const connectionStatus = db.runCommand({ connectionStatus: 1 });
printjson({
    Status: "Conexión Exitosa a MongoDB",
    Database: connectionStatus.authInfo.authenticatedUserRoles[0]?.db ?? "starbucks_transactions",
    User: connectionStatus.authInfo.authenticatedUsers[0]?.user ?? "rootuser"
});

// 2. Mostrar Colecciones (el equivalente a SHOW TABLES)
print("\n--- Colecciones Disponibles ---");
const collections = db.getCollectionNames();
collections.forEach(function(name) {
    print(`| ${name} |`);
});

// 3. Ejecutar una consulta de prueba simple (contar documentos en una colección existente, si tienes una)
// ASUMIMOS que tienes una colección llamada 'ordenes' (o 'transactions') en tu DB de inicialización.
try {
    const count = db.ticket.countDocuments({});
    print(`\n--- Conteo de Documentos ---`);
    print(`La colección 'ticket' contiene ${count} documentos.`);
} catch (e) {
    print(`\n--- Conteo de Documentos ---`);
    print("Nota: No se pudo contar documentos. Asegúrate de que la colección 'ticket' exista.");
}



print("\n\nQuery de total vendido por sucursal id...")
print(
db.ticket.aggregate([
    // 1. Filtrar los tickets por la lista de IDs de sucursal
    {
        $match: {
            sucursal_id: { $in: [2,4] }
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
]).forEach(printjson)
);

print("\n\nQuery de todo Ticket")
print(db.ticket.find());