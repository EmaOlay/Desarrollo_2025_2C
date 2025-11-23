// Script de prueba para verificar la conectividad y consultar todas las colecciones.

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
collections.forEach(function (name) {
    print(`| ${name} |`);
});

// 3. Consultar cada una de las colecciones
print("\n--- Contenido de la colección 'ticket' ---");
printjson(db.ticket.find().toArray());
print("\n--- Cantidad de documentos de la colección 'ticket' ---");
printjson(db.ticket.find().count());

print("\n--- Contenido de la colección 'interaccion' ---");
printjson(db.interaccion.find().toArray());

print("\n--- Contenido de la colección 'canje' ---");
printjson(db.canje.find().toArray());

print("\n--- Contenido de la colección 'MenuDiaCache' ---");
printjson(db.MenuDiaCache.find().toArray());