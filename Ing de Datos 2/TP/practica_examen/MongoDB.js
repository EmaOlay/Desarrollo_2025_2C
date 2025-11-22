// MongoDB Exercise: IoT Platform Event Management

// 1) Entidades (Collection Design)
// I will design a single 'devices' collection to store information about each device,
// including its zone and an array of its events. This denormalized approach
// is efficient for retrieving device-specific information and recent events.
// The 'en_alarma' field will be at the device level for quick status checks.

// Collection: devices
/*
{
    _id: ObjectId("6564e52f1b4c3e8a7b1d1e2f"), // Device ID
    device_name: "Sensor de Temperatura 01",
    zone: "Planta Industrial",
    en_alarma: false, // Flag to indicate if the device has registered a 'fallo' event
    events: [
        {
            event_id: ObjectId(),
            timestamp: ISODate("2023-11-20T10:00:00Z"),
            event_type: "lectura", // lectura, alerta, fallo
            measured_value: 25.5,
            unit_of_measure: "°C"
        },
        {
            event_id: ObjectId(),
            timestamp: ISODate("2023-11-21T11:30:00Z"),
            event_type: "alerta",
            measured_value: 80,
            unit_of_measure: "%"
        }
    ]
}
*/

// 2) Inserts (Sample Data)
db.devices.drop(); // Clear existing data for demonstration

db.devices.insertMany([
    {
        _id: ObjectId("6564e52f1b4c3e8a7b1d1e01"),
        device_name: "Sensor Temp A",
        zone: "Planta Industrial",
        en_alarma: false,
        events: [
            {
                event_id: ObjectId(),
                timestamp: ISODate("2023-11-25T08:00:00Z"),
                event_type: "lectura",
                measured_value: 28.1,
                unit_of_measure: "°C"
            },
            {
                event_id: ObjectId(),
                timestamp: ISODate("2023-11-26T09:00:00Z"),
                event_type: "lectura",
                measured_value: 31.0,
                unit_of_measure: "°C"
            },
            {
                event_id: ObjectId(),
                timestamp: ISODate("2023-11-27T10:00:00Z"),
                event_type: "alerta",
                measured_value: 95,
                unit_of_measure: "%"
            }
        ]
    },
    {
        _id: ObjectId("6564e52f1b4c3e8a7b1d1e02"),
        device_name: "Cámara Seguridad 01",
        zone: "Planta Industrial",
        en_alarma: true, // Marked true because of a 'fallo' event
        events: [
            {
                event_id: ObjectId(),
                timestamp: ISODate("2023-11-24T12:00:00Z"),
                event_type: "lectura",
                measured_value: 1,
                unit_of_measure: "V"
            },
            {
                event_id: ObjectId(),
                timestamp: ISODate("2023-11-26T13:00:00Z"),
                event_type: "fallo",
                measured_value: 0,
                unit_of_measure: "Error"
            }
        ]
    },
    {
        _id: ObjectId("6564e52f1b4c3e8a7b1d1e03"),
        device_name: "Medidor Eléctrico 01",
        zone: "Oficina Central",
        en_alarma: false,
        events: [
            {
                event_id: ObjectId(),
                timestamp: ISODate("2023-11-25T14:00:00Z"),
                event_type: "lectura",
                measured_value: 220,
                unit_of_measure: "V"
            },
            {
                event_id: ObjectId(),
                timestamp: ISODate("2023-11-26T15:00:00Z"),
                event_type: "lectura",
                measured_value: 221,
                unit_of_measure: "V"
            }
        ]
    },
    {
        _id: ObjectId("6564e52f1b4c3e8a7b1d1e04"),
        device_name: "Sensor Temp B",
        zone: "Data Center",
        en_alarma: false,
        events: [
            {
                event_id: ObjectId(),
                timestamp: ISODate("2023-11-26T16:00:00Z"),
                event_type: "lectura",
                measured_value: 35.2,
                unit_of_measure: "°C"
            }
        ]
    },
    {
        _id: ObjectId("6564e52f1b4c3e8a7b1d1e05"),
        device_name: "Sensor Fallo A",
        zone: "Oficina Central",
        en_alarma: true,
        events: [
            {
                event_id: ObjectId(),
                timestamp: ISODate("2023-11-27T09:30:00Z"),
                event_type: "fallo",
                measured_value: 1,
                unit_of_measure: "Error"
            }
        ]
    }
]);

// 3) Respuestas de caso de uso (MongoDB Queries)

// Query 6: ¿Qué dispositivos pertenecen a la zona "Planta Industrial"?
// Explanation: This query uses a simple 'find' operation to select documents
// where the 'zone' field matches "Planta Industrial".
print("--- Query 6: Dispositivos en 'Planta Industrial' ---");
db.devices.find(
    { zone: "Planta Industrial" },
    { device_name: 1, zone: 1, _id: 0 } // Project only device_name and zone, exclude _id
);

// Query 7: ¿Qué dispositivos registraron al menos un evento de tipo "fallo"?
// Explanation: This query uses an aggregation pipeline.
// $unwind: Deconstructs the 'events' array field from the input documents to output a document for each element.
// $match: Filters the documents to include only those where 'event_type' is "fallo".
// $group: Groups the results by '_id' (device ID) to get unique devices, and uses $first to get device_name.
print("\n--- Query 7: Dispositivos con al menos un evento de tipo 'fallo' ---");
db.devices.aggregate([
    { $unwind: "$events" },
    { $match: { "events.event_type": "fallo" } },
    { $group: { _id: "$_id", device_name: { $first: "$device_name" } } },
    { $project: { _id: 0, device_name: 1 } } // Project only device_name
]);

// Alternatively, using $elemMatch for a more direct approach without $unwind:
// This approach is generally more efficient as it avoids duplicating documents.
print("\n--- Query 7 (Alternative): Dispositivos con al menos un evento de tipo 'fallo' (using $elemMatch) ---");
db.devices.find(
    { "events.event_type": "fallo" },
    { device_name: 1, _id: 0 }
);


// Query 8: ¿Qué dispositivos tuvieron eventos de tipo "alerta" o "fallo"?
// Explanation: Similar to Query 7, this uses $unwind and $match, but with an $in operator
// to check for multiple event types.
print("\n--- Query 8: Dispositivos con eventos de tipo 'alerta' o 'fallo' ---");
db.devices.aggregate([
    { $unwind: "$events" },
    { $match: { "events.event_type": { $in: ["alerta", "fallo"] } } },
    { $group: { _id: "$_id", device_name: { $first: "$device_name" } } },
    { $project: { _id: 0, device_name: 1 } }
]);

// Alternatively, using $elemMatch:
print("\n--- Query 8 (Alternative): Dispositivos con eventos de tipo 'alerta' o 'fallo' (using $elemMatch) ---");
db.devices.find(
    { "events.event_type": { $in: ["alerta", "fallo"] } },
    { device_name: 1, _id: 0 }
);


// Query 9: ¿Qué dispositivos se encuentran actualmente marcados con en_alarma: true?
// Explanation: This query directly filters documents based on the top-level 'en_alarma' field,
// which is designed for quick access to this status.
print("\n--- Query 9: Dispositivos actualmente marcados con en_alarma: true ---");
db.devices.find(
    { en_alarma: true },
    { device_name: 1, zone: 1, en_alarma: 1, _id: 0 }
);


// Query 10: ¿Qué dispositivos registraron valores de temperatura mayores o iguales a 30 °C en los últimos 3 días?
// Explanation: This query involves filtering by event type, unit of measure, value, and timestamp.
// It calculates the date 3 days ago from the current date.
// $unwind: Deconstructs the 'events' array.
// $match: Filters events based on timestamp (last 3 days), event_type, unit_of_measure, and measured_value.
// $group: Groups by device to ensure unique device names are returned.
// $project: Projects only the device_name.
print("\n--- Query 10: Dispositivos con temperatura >= 30 °C en los últimos 3 días ---");
var threeDaysAgo = new Date();
threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);

db.devices.aggregate([
    { $unwind: "$events" },
    { $match: {
        "events.timestamp": { $gte: threeDaysAgo },
        "events.event_type": "lectura",
        "events.unit_of_measure": "°C",
        "events.measured_value": { $gte: 30 }
    }},
    { $group: { _id: "$_id", device_name: { $first: "$device_name" } } },
    { $project: { _id: 0, device_name: 1 } }
]);
