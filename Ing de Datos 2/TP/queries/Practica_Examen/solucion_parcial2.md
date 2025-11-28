# Solución del Ejercicio de Práctica 2 - Parcial

## Ejercicio 1: Plataforma Musical (Cassandra)

Se resuelve el **Caso de Uso 2**: Consultar las canciones reproducidas por un usuario dentro de un género específico, ordenadas por fecha de reproducción.

### a. Diseño de la Tabla (CREATE TABLE)

Para optimizar la consulta, la clave de partición debe incluir al usuario y al género para que todas las canciones que un usuario escucha de un género específico estén en la misma partición. La clave de clustering será la fecha de reproducción para ordenar las canciones cronológicamente.

```cql
CREATE TABLE reproducciones_por_genero (
    id_usuario UUID,
    genero TEXT,
    fecha_reproduccion TIMESTAMP,
    nombre_cancion TEXT,
    nombre_artista TEXT,
    nombre_album TEXT,
    PRIMARY KEY ((id_usuario, genero), fecha_reproduccion)
) WITH CLUSTERING ORDER BY (fecha_reproduccion DESC);
```

### b. Instancia de Datos (INSERT)

Se insertan 4 ejemplos de reproducciones para el usuario `Emanuel` en diferentes géneros.

```cql
INSERT INTO reproducciones_por_genero (id_usuario, genero, fecha_reproduccion, nombre_cancion, nombre_artista, nombre_album) VALUES (a1b2c3d4-e5f6-7890-1234-567890abcdef, 'Rock Clásico', '2025-11-28T10:00:00Z', 'Stairway to Heaven', 'Led Zeppelin', 'Led Zeppelin IV');
INSERT INTO reproducciones_por_genero (id_usuario, genero, fecha_reproduccion, nombre_cancion, nombre_artista, nombre_album) VALUES (a1b2c3d4-e5f6-7890-1234-567890abcdef, 'Pop Latino', '2025-11-28T10:05:00Z', 'La Flaca', 'Jarabe De Palo', 'La Flaca');
INSERT INTO reproducciones_por_genero (id_usuario, genero, fecha_reproduccion, nombre_cancion, nombre_artista, nombre_album) VALUES (a1b2c3d4-e5f6-7890-1234-567890abcdef, 'Rock Clásico', '2025-11-27T15:30:00Z', 'Bohemian Rhapsody', 'Queen', 'A Night at the Opera');
INSERT INTO reproducciones_por_genero (id_usuario, genero, fecha_reproduccion, nombre_cancion, nombre_artista, nombre_album) VALUES (a1b2c3d4-e5f6-7890-1234-567890abcdef, 'Rock Nacional', '2025-11-28T11:00:00Z', 'Seminare', 'Serú Girán', 'Serú Girán');
```

### c. Consulta CQL y Resultado

La consulta filtra por `id_usuario` y `genero` para obtener las canciones del género "Rock Clásico" escuchadas por el usuario. El orden descendente por fecha ya está definido en el esquema de la tabla.

**Consulta:**
```cql
SELECT fecha_reproduccion, nombre_cancion, nombre_artista
FROM reproducciones_por_genero
WHERE id_usuario = a1b2c3d4-e5f6-7890-1234-567890abcdef AND genero = 'Rock Clásico';
```

**Resultado Devuelto:**
```
 fecha_reproduccion         | nombre_cancion      | nombre_artista
----------------------------+---------------------+----------------
 2025-11-28 10:00:00+0000   | Stairway to Heaven  | Led Zeppelin
 2025-11-27 15:30:00+0000   | Bohemian Rhapsody   | Queen
(2 rows)
```

### d. Valor del Token

El token se calcula sobre la clave de partición, que en este caso es `(a1b2c3d4-e5f6-7890-1234-567890abcdef, 'Rock Clásico')`.

**CQL para consultar el token:**
```cql
SELECT token(id_usuario, genero)
FROM reproducciones_por_genero
WHERE id_usuario = a1b2c3d4-e5f6-7890-1234-567890abcdef AND genero = 'Rock Clásico'
LIMIT 1;
```
---

## Ejercicio 2: Clínica Médica (MongoDB)

### Diseño de la Colección

Se propone una colección principal `pacientes`. Cada documento contendrá la información del paciente y un array de sub-documentos con sus `estudios`. Esto permite mantener toda la información de un paciente unificada y facilita las consultas.

**Ejemplo de Documento en la colección `pacientes`:**
```json
{
  "dni": "12345678",
  "nombre_completo": "Juan Carlos Pérez",
  "obra_social": "OSDE",
  "medico_cabecera": "Dr. House",
  "riesgo": true,
  "estudios": [
    {
      "fecha_realizacion": ISODate("2025-11-15T09:00:00Z"),
      "tipo_estudio": "Análisis",
      "resultado_numerico": 210,
      "unidad_medida": "mg/dL",
      "observacion": "Glucosa elevada."
    },
    {
      "fecha_realizacion": ISODate("2025-10-02T08:30:00Z"),
      "tipo_estudio": "Radiografía",
      "observacion": "Sin particularidades."
    }
  ]
}
```

### Consultas

**1. ¿Qué pacientes pertenecen a la obra social "OSDE"?**
```javascript
db.pacientes.find(
    { obra_social: "OSDE" },
    { nombre_completo: 1, dni: 1 }
);
```

**2. ¿Qué pacientes se realizaron al menos un estudio de tipo "Radiografía"?**
```javascript
db.pacientes.find(
    { "estudios.tipo_estudio": "Radiografía" },
    { nombre_completo: 1, dni: 1 }
);
```

**3. ¿Qué pacientes tienen estudios de tipo "Análisis" o "Resonancia"?**
```javascript
db.pacientes.find(
    { "estudios.tipo_estudio": { $in: ["Análisis", "Resonancia"] } },
    { nombre_completo: 1, obra_social: 1 }
);
```

**4. ¿Qué pacientes están marcados con la clave `riesgo: true`?**
```javascript
db.pacientes.find(
    { riesgo: true },
    { nombre_completo: 1, medico_cabecera: 1 }
);
```

**5. ¿Qué pacientes tuvieron resultados de glucosa mayores o iguales a 200 mg/dL?**
```javascript
db.pacientes.find({
  "estudios": {
    $elemMatch: {
      "resultado_numerico": { $gte: 200 },
      "unidad_medida": "mg/dL",
      "observacion": /glucosa/i // Búsqueda flexible por si la observación varía
    }
  }
});
```
