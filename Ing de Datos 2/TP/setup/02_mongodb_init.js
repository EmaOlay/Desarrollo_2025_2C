/**
 * Script de Inicialización e Indexación para MongoDB
 * Bases de Datos Políglotas (Capa Transaccional)
 *
 * Ejecutar en la mongo-shell (o mongosh)
 * > mongosh --file mongo_init_script.js
 */

// Usar la base de datos (creará una si no existe)
use("starbucks_transactions");

print("Limpiando colecciones existentes...");
db.ticket.drop();
db.interaccion.drop();
db.menudiacache.drop();
db.canje.drop();

print("--- 1. Creando Colecciones (si no existen) ---");

// Aunque MongoDB crea colecciones implícitamente, podemos crearlas explícitamente si queremos opciones.
db.createCollection("ticket");
db.createCollection("interaccion");
db.createCollection("canje");
db.createCollection("MenuDiaCache");

print("--- 2. Creando Índices ---");

// =========================================================================================
// COLECCIÓN: TICKET (Para transacciones y reportes rápidos)
// =========================================================================================

// Índice 1: Para búsquedas rápidas por sucursal y fecha (común para reportes)
db.Ticket.createIndex({ sucursal_id: 1, fecha: -1 }, { name: "idx_sucursal_fecha" });

// Índice 2: Para búsquedas por campos denormalizados críticos (ejemplo: buscar todos los tickets de un cliente para lineage)
db.Ticket.createIndex({ cliente_id: 1 }, { name: "idx_cliente_id" });

// Índice 3: Para acelerar consultas que filtran por la ciudad (campo denormalizado)
db.Ticket.createIndex({ sucursal_ciudad: 1 }, { name: "idx_sucursal_ciudad" });

// Índice 4: Índice Multi-clave para soportar búsquedas en el array 'detalles'
// Esto optimiza búsquedas como la de "Latte Vainilla" que hicimos en el ejemplo.
db.Ticket.createIndex({ "detalles.nombre_producto": 1 }, { name: "idx_detalles_producto" });


// =========================================================================================
// COLECCIÓN: INTERACCION (Para eventos y análisis de sentimiento/reseñas)
// =========================================================================================

// Índice 5: Para encontrar interacciones de un cliente en un período de tiempo
db.Interaccion.createIndex({ cliente_id: 1, fecha: -1 }, { name: "idx_cliente_fecha_interaccion" });

// Índice 6: Para reportes de baja calificación (filtrando en el subdocumento metadata)
db.Interaccion.createIndex({ "metadata.score": 1 }, { name: "idx_metadata_score" });


// =========================================================================================
// COLECCIÓN: CANJE (Para análisis del programa de lealtad)
// =========================================================================================

// Índice 7: Búsquedas por cliente y fecha de canje
db.canje.createIndex({ cliente_id: 1, fecha_canje: -1 }, { name: "idx_cliente_fecha_canje" });

// Índice 8: Búsquedas por el ítem canjeado
db.canje.createIndex({ item_canjeado: 1 }, { name: "idx_item_canjeado" });


// =========================================================================================
// COLECCIÓN: MENUDIACACHE (Cache con TTL)
// =========================================================================================

// Índice 9: Índice TTL (Time-To-Live)
// Hace que los documentos en esta colección expiren automáticamente 1 hora (3600 segundos)
// después de la 'fecha_creacion', tal como lo definiste en el DER.
db.MenuDiaCache.createIndex(
  { fecha_creacion: 1 },
  { expireAfterSeconds: 3600, name: "idx_ttl_1hr" }
);

// Índice 10: Para desestructurar y buscar eficientemente productos por su tipo
db.MenuDiaCache.createIndex({ "productos.tipo": 1 }, { name: "idx_productos_tipo" });


print("--- 3. Inicialización de datos de prueba (Opcional) ---");

// A. Colección 'ticket' (Transacciones)
db.ticket.insertMany([
    {
        ticket_id: 1,
        sucursal_id: 2,
        cliente_id: 1,
        fecha: ISODate("2024-09-01T08:30:00Z"), // Ordenes por (fecha, sucursal)
        total: 6,
        metodo_pago: 'Efectivo',
        promocion_id: 1,
        detalles: [
            { product_id: 1, cantidad: 2, precio: 3 } // Latte Grande
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
            { product_id: 2, cantidad: 1, precio: 7 } // Muffin
        ]
    },
    {
        ticket_id: 3,
        sucursal_id: 3,
        cliente_id: 1,
        fecha: ISODate("2025-09-01T09:00:00Z"), // Misma fecha, diferente hora
        total: 32,
        metodo_pago: 'Efectivo',
        promocion_id: 1,
        detalles: [
            { product_id: 1, cantidad: 2, precio: 16 }, // Latte Grande
            { product_id: 2, cantidad: 1, precio: 5 },  // Muffin
            { product_id: 3, cantidad: 1, precio: 5 }   // Capuccino Chico
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
            { product_id: 3, cantidad: 2, precio: 16 } // Capuccino Chico
        ]
    },
        {
        ticket_id: 57,
        sucursal_id: 3,
        cliente_id: 1,
        fecha: ISODate("2025-09-01T15:00:00Z"),
        total: 15,
        metodo_pago: 'Efectivo',
        promocion_id: 1,
        detalles: [
            { product_id: 3, cantidad: 2, precio: 16 },
            { product_id: 2, cantidad: 1, precio: 1} // Capuccino Chico
        ]
    },
]);

db.Ticket.insertOne({
  ticket_id: "TKT-2025-001",
  cliente_id: 101,
  cliente_nombre: "Ana Garcia",
  sucursal_id: 3,
  sucursal_ciudad: "Buenos Aires",
  fecha: new Date("2025-11-05T10:30:00Z"),
  total: 6.50,
  metodo_pago: "Tarjeta",
  promocion_id: 201,
  nombre_promocion: "Desc. Mañana",
  detalles: [
    { producto_id: 1, nombre_producto: "Latte", precio_historico: 4.50, cantidad: 1 },
    { producto_id: 2, nombre_producto: "Muffin", precio_historico: 2.00, cantidad: 1 }
  ]
});

db.Interaccion.insertOne({
  cliente_id: 102,
  cliente_email: "juan.perez@email.com",
  tipo_evento: "Reseña Producto",
  fecha: new Date(),
  metadata: {
    producto_id: 1,
    nombre_producto: "Latte",
    score: 1,
    comentario: "Sabor muy aguado. Decepcionado." // Comentario corto (menos de 10 palabras)
  }
});

db.canje.insertOne({
  cliente_id: 2,
  cliente_stars_antes: 1200,
  fecha_canje: new Date(),
  stars_usadas: 800,
  item_canjeado: "Taza Premium",
  valor_estimado: 15.00
});

db.MenuDiaCache.insertOne({
  sucursal_id: 1,
  fecha_creacion: new Date(),
  productos: [
    { producto_id: 1, nombre: "Latte", precio_actual: 4.80, tipo: "Bebida Caliente" },
    { producto_id: 2, nombre: "Muffin", precio_actual: 3.50, tipo: "Panadería/Pasteleria" },
    { producto_id: 3, nombre: "Frappuccino", precio_actual: 5.50, tipo: "Bebida Fria" }
  ]
});

print("--- Inicialización y indexación completada. ---");