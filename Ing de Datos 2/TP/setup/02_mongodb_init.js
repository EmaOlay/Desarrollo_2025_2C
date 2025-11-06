// setup/02_mongodb_init.js
// Script de inicialización para MongoDB (Base de datos: starbucks_transactions)

// use starbucks_transactions; // No se usa se pasa como argumento del string connection

// -----------------------------------------------------------
// 1. ELIMINAR COLECCIONES PREVIAS (Idempotencia)
// -----------------------------------------------------------
print("Limpiando colecciones existentes...");
db.ticket.drop();
db.interaccion.drop();
db.menudiacache.drop();
db.canje.drop();

// -----------------------------------------------------------
// 2. Insertar datos de ejemplo y crear las colecciones
// -----------------------------------------------------------

// A. Colección 'ticket' (Transacciones)
db.ticket.insertMany([
    {
        ticket_id: 1,
        sucursal_id: 1,
        cliente_id: 1,
        fecha: ISODate("2024-09-01T08:30:00Z"), // Ordenes por (fecha, sucursal)
        total: 6,
        metodo_pago: 'Efectivo',
        promocion_id: 1,
        detalles: [
            { product_id: 501, cantidad: 2, precio: 3 } // Latte Grande
        ]
    },
    {
        ticket_id: 2,
        sucursal_id: 102,
        cliente_id: 2,
        fecha: ISODate("2025-09-01T08:30:00Z"),
        total: 7,
        metodo_pago: 'Tarjeta',
        promocion_id: 2,
        detalles: [
            { product_id: 502, cantidad: 1, precio: 7 } // Muffin
        ]
    },
    {
        ticket_id: 3,
        sucursal_id: 102,
        cliente_id: 1,
        fecha: ISODate("2025-09-01T09:00:00Z"), // Misma fecha, diferente hora
        total: 32,
        metodo_pago: 'Efectivo',
        promocion_id: 1,
        detalles: [
            { product_id: 501, cantidad: 2, precio: 16 }, // Latte Grande
            { product_id: 502, cantidad: 1, precio: 5 },  // Muffin
            { product_id: 503, cantidad: 1, precio: 5 }   // Capuccino Chico
        ] // Cliente 1 compra 3 productos distintos (para práctica de agregación)
    },
    {
        ticket_id: 4,
        sucursal_id: 101,
        cliente_id: 2,
        fecha: ISODate("2025-09-02T15:00:00Z"),
        total: 32,
        metodo_pago: 'Efectivo',
        promocion_id: 1,
        detalles: [
            { product_id: 503, cantidad: 2, precio: 16 } // Capuccino Chico
        ]
    },
]);


// D. COLECCIÓN NUEVA: 'interaccion' (Eventos de Comportamiento)
db.interaccion.insertMany([
    {
        cliente_id: 2,
        tipo_evento: "ProductView",
        fecha: ISODate("2025-11-05T08:00:00Z"),
        metadata: { product_id: 503, source: "App Móvil" }
    },
    {
        cliente_id: 1,
        tipo_evento: "Review",
        fecha: ISODate("2025-11-05T15:30:00Z"),
        metadata: { product_id: 501, score: 5, comentario: "El mejor latte que he probado." }
    },
    {
        cliente_id: 2,
        tipo_evento: "Search",
        fecha: ISODate("2025-11-06T09:10:00Z"),
        metadata: { busqueda: "Muffin de Arándanos", resultados: 1 }
    }
]);
print("Colección interaccion inicializada.");


// E. COLECCIÓN NUEVA: 'menudiacache' (Caché con TTL)
db.menudiacache.insertMany([
    {
        sucursal_id: 101,
        fecha_creacion: ISODate("2025-11-06T19:00:00Z"), // Creado hace poco
        nombre_menu: "Menú Espresso Express",
        productos_ids: [501, 502],
        precio_promocional: 6.99
    },
    {
        sucursal_id: 102,
        fecha_creacion: ISODate("2025-11-05T09:30:00Z"), // Creado ayer, ideal para TTL
        nombre_menu: "Menú Desayuno Completo",
        productos_ids: [502, 503],
        precio_promocional: 9.50
    }
]);
print("Colección menudiacache inicializada con datos de caché.");


// F. COLECCIÓN NUEVA: 'canje' (Recompensas - Canjes por cliente, fecha)
db.canje.insertMany([
    {
        cliente_id: 2,
        fecha_canje: ISODate("2025-10-15T11:00:00Z"), // Canjes por (cliente, fecha)
        stars_usadas: 100,
        item_canjeado: "Bebida Gratis de cualquier tamaño"
    },
    {
        cliente_id: 1,
        fecha_canje: ISODate("2025-11-01T12:00:00Z"),
        stars_usadas: 50,
        item_canjeado: "Snack a mitad de precio"
    }
]);
print("Colección canje inicializada.");


// -----------------------------------------------------------
// 3. Crear índices
// -----------------------------------------------------------

// Índices del Usuario
db.ticket.createIndex({ ticket_id: 1 }, { unique: true });
db.stores.createIndex({ store_id: 1 }, { unique: true });
db.products.createIndex({ product_id: 1 }, { unique: true });

// Índices para Requerimientos
db.ticket.createIndex({ cliente_id: 1 });
db.ticket.createIndex({ sucursal_id: 1, fecha: -1 }); // Órdenes por (fecha, sucursal)

db.canje.createIndex({ cliente_id: 1, fecha_canje: -1 }); // Canjes por (cliente, fecha)

// Índice TTL para Caché de Menú del Día (Elimina documentos 1 hora después de la creación)
db.menudiacache.createIndex({ fecha_creacion: 1 }, { expireAfterSeconds: 3600 }); // 
db.menudiacache.createIndex({ sucursal_id: 1 });

db.interaccion.createIndex({ cliente_id: 1, fecha: -1 }); // Para analítica de comportamiento

print("Índices creados exitosamente, incluyendo el índice TTL.");
// Fin de la inicialización