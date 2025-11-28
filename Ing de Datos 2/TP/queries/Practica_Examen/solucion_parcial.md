# Solución del Ejercicio de Práctica - Parcial

## Ejercicio 1: Plataforma de Educación Online (Cassandra)

Se resuelve el **Caso de Uso 1**: Listar los comentarios de los estudiantes sobre un curso, filtrados por calificación (por ejemplo, solo los de 5 estrellas), ordenados por fecha.

### a. Diseño de la Tabla (CREATE TABLE)

Para optimizar la consulta, la clave primaria debe permitir filtrar por curso y calificación. La clave de partición será `(nombre_curso, calificacion)` para que todos los comentarios de una misma calificación para un curso estén en la misma partición. La clave de clustering será `fecha_comentario` para ordenar los comentarios cronológicamente.

```cql
CREATE TABLE comentarios_por_curso (
    nombre_curso TEXT,
    calificacion INT,
    fecha_comentario TIMESTAMP,
    nombre_estudiante TEXT,
    comentario TEXT,
    PRIMARY KEY ((nombre_curso, calificacion), fecha_comentario)
) WITH CLUSTERING ORDER BY (fecha_comentario DESC);
```

### b. Instancia de Datos (INSERT)

Se insertan 5 comentarios de ejemplo para el curso "Ingeniería de Datos" con distintas calificaciones.

```cql
INSERT INTO comentarios_por_curso (nombre_curso, calificacion, fecha_comentario, nombre_estudiante, comentario) VALUES ('Ingeniería de Datos', 5, '2025-10-05T10:00:00Z', 'Ana García', '¡Excelente curso! Muy completo.');
INSERT INTO comentarios_por_curso (nombre_curso, calificacion, fecha_comentario, nombre_estudiante, comentario) VALUES ('Ingeniería de Datos', 4, '2025-10-06T11:30:00Z', 'Juan Pérez', 'Buen contenido, pero podría ser más práctico.');
INSERT INTO comentarios_por_curso (nombre_curso, calificacion, fecha_comentario-network', 'Excelente curso, muy práctico y fácil de seguir.');
INSERT INTO comentarios_por_curso (nombre_curso, calificacion, fecha_comentario, nombre_estudiante, comentario) VALUES ('Ingeniería de Datos', 5, '2025-10-07T12:00:00Z', 'María López', '¡Lo mejor que he visto sobre el tema!');
INSERT INTO comentarios_por_curso (nombre_curso, calificacion, fecha_comentario, nombre_estudiante, comentario) VALUES ('Bases de Datos', 5, '2025-10-08T14:00:00Z', 'Carlos Ruiz', 'Muy buen curso introductorio.');
```

### c. Consulta CQL y Resultado

La consulta filtra por `nombre_curso` y `calificacion` para obtener los comentarios de 5 estrellas. El orden descendente por fecha ya está definido en el esquema de la tabla.

**Consulta:**
```cql
SELECT fecha_comentario, nombre_estudiante, comentario
FROM comentarios_por_curso
WHERE nombre_curso = 'Ingeniería de Datos' AND calificacion = 5;
```

**Resultado Devuelto:**
```
 fecha_comentario         | nombre_estudiante | comentario
--------------------------+-------------------+------------------------------------------
 2025-10-07 12:00:00+0000 |      María López  | ¡Lo mejor que he visto sobre el tema!
 2025-10-05 10:00:00+0000 |       Ana García  | ¡Excelente curso! Muy completo.
(2 rows)
```

### d. Valor del Token

El token se calcula sobre la clave de partición, que en este caso es `('Ingeniería de Datos', 5)`. El valor del token determina en qué nodo del clúster de Cassandra se almacenan los datos de esta partición.

**CQL para consultar el token:**
```cql
SELECT token(nombre_curso, calificacion)
FROM comentarios_por_curso
WHERE nombre_curso = 'Ingeniería de Datos' AND calificacion = 5
LIMIT 1;
```
---

## Ejercicio 2: Red de Dispositivos IoT (MongoDB)

### Diseño de la Colección

Se propone una única colección llamada `dispositivos`. Cada documento representará un dispositivo y contendrá un array de eventos para mantener la atomicidad de las operaciones a nivel de dispositivo. La clave `en_alarma` se actualizará a `true` si el dispositivo reporta un fallo.

**Ejemplo de Documento en la colección `dispositivos`:**
```json
{
  "_id": "TEMP-001",
  "zona": "Planta Industrial",
  "tipo_dispositivo": "sensor_temperatura",
  "en_alarma": true,
  "eventos": [
    {
      "fecha_hora": ISODate("2025-11-20T10:00:00Z"),
      "tipo_evento": "lectura",
      "valor": 32,
      "unidad_medida": "°C"
    },
    {
      "fecha_hora": ISODate("2025-11-21T15:30:00Z"),
      "tipo_evento": "fallo",
      "valor": null,
      "unidad_medida": null
    }
  ]
}
```

### Consultas

**1. ¿Qué dispositivos pertenecen a la zona "Planta Industrial"?**
```javascript
db.dispositivos.find(
    { zona: "Planta Industrial" },
    { _id: 1, tipo_dispositivo: 1 }
);
```

**2. ¿Qué dispositivos registraron al menos un evento de tipo "fallo"?**
```javascript
db.dispositivos.find(
    { "eventos.tipo_evento": "fallo" },
    { _id: 1, zona: 1 }
);
```

**3. ¿Qué dispositivos tuvieron eventos de tipo "alerta" o "fallo"?**
```javascript
db.dispositivos.find(
    { "eventos.tipo_evento": { $in: ["alerta", "fallo"] } },
    { _id: 1, zona: 1 }
);
```

**4. ¿Qué dispositivos se encuentran actualmente marcados con `en_alarma: true`?**
```javascript
db.dispositivos.find(
    { en_alarma: true },
    { _id: 1, zona: 1, tipo_dispositivo: 1 }
);
```

**5. ¿Qué dispositivos registraron valores de temperatura mayores o iguales a 30 °C en los últimos 3 días?**
```javascript
// Se asume que la fecha actual es 2025-11-28
var tres_dias_atras = new Date();
tres_dias_atras.setDate(tres_dias_atras.getDate() - 3);

db.dispositivos.find({
  $and: [
    { "tipo_dispositivo": "sensor_temperatura" },
    { "eventos": {
        $elemMatch: {
          "fecha_hora": { $gte: tres_dias_atras },
          "valor": { $gte: 30 },
          "unidad_medida": "°C"
        }
      }
    }
  ]
});
```
