// queries/test_mongodb.js
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
    const count = db.ordenes.countDocuments({});
    print(`\n--- Conteo de Documentos ---`);
    print(`La colección 'ordenes' contiene ${count} documentos.`);
} catch (e) {
    print(`\n--- Conteo de Documentos ---`);
    print("Nota: No se pudo contar documentos. Asegúrate de que la colección 'ordenes' exista.");
}