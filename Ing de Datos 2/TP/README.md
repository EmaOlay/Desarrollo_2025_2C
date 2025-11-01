# ☕ TP Ingeniería de Datos II: Starbucks Políglota

## 📝 Descripción del Proyecto

Este proyecto implementa una arquitectura de datos políglota para simular los sistemas de información de una cadena de cafeterías (Starbucks). El objetivo es utilizar la base de datos más adecuada para cada tipo de dato y necesidad de negocio, incluyendo gestión de catálogos, transacciones, datos de fidelización y análisis relacional.

El *setup* completo se orquesta mediante **Docker Compose**, y se incluye una **Interfaz de Usuario de Texto (TUI)** para demostrar la funcionalidad de las consultas en cada motor de base de datos.

## 🚀 Arquitectura Políglota (Servicios)

| Servicio | Tecnología | Propósito |
| :--- | :--- | :--- |
| **`mysql`** | MySQL/MariaDB | **Maestro/Relacional:** Gestión de catálogos (`Producto`, `Sucursal`, `Cliente`) y datos de fidelización. |
| **`mongodb`** | MongoDB | **Transaccional/Documental:** Almacenamiento de órdenes de compra y transacciones históricas detalladas. |
| **`cassandra`** | Apache Cassandra | **Analítica/Series de Tiempo:** Registro de eventos de canje de puntos y logs de sistema. |
| **`neo4j`** | Neo4j | **Grafos:** Análisis de relaciones complejas (ej. "Clientes que compraron productos recomendados por otros clientes"). |
| **`redis`** | Redis | **Cache:** Almacenamiento volátil para la sesión del usuario o *cache* de menús. |
| **`cli`** | Python (Rich) | **Interfaz TUI:** Herramienta para ejecutar y demostrar las *queries* de negocio en cada BD. |
| **`setup_service`** | Bash/Python/Shells de BD | **Inicialización:** Script que espera por la disponibilidad de todas las BD e inyecta los datos iniciales y la estructura. |

## 📦 Estructura del Proyecto

```
├── TP main
│   ├── cli                                 # Código fuente de la Interfaz TUI (Python)
│   │   ├── cli.py                          # Lógica principal de la TUI
│   │   └── Dockerfile                      # Dockerfile para construir el entorno CLI
│   ├── DER.png                             # Diagrama Entidad-Relación del proyecto
│   ├── DER.puml                            # Fuente del diagrama (PlantUML)
│   ├── docker-compose.yml                  # Definición de todos los servicios
│   ├── queries
│   │   ├── productos_sin_stock_global.sql
│   │   ├── promociones_activas_hoy.sql
│   │   └── prueba.sql                      # Ejemplo de consulta que muestra tablas e info de MySQL
│   ├── README.md
│   └── setup
│       ├── 01_mysql_init.sql               # Codigo sql a ejecutar para inicializar la DB MySQL
│       ├── 02_mongodb_init.js              # Codigo js a ejecutar para inicializar la DB MongoDB
│       ├── 03_cassandra_init.cql           # Codigo cql a ejecutar para inicializar la DB Cassandra
│       ├── 04_neo4j_init.cypher            # Codigo cypher a ejecutar para inicializar la DB Neo4j
│       ├── 05_redis_config.conf            # Codigo config de redis
│       ├── Dockerfile                      # Dockerfile para construir el entorno setup-service
│       ├── init_all_dbs.sh                 # script para ejecutar inits
│       └── wait-for-it.sh                  # wait script para no ejecutar sobre DBs que no estan listas
```

## ⚙️ Configuración y Ejecución

### Requisitos

  * Docker (v20.10.0+)
  * Docker Compose (v2.0.0+)

### Pasos de Ejecución

1.  **Construir y Lanzar los Contenedores:**
    Este comando construye la imagen `cli` y levanta todos los servicios, incluido el `setup_service` que inicializará las bases de datos.

    ```bash
    docker compose up --build
    ```

2.  **Verificar el Estado:**
    Asegúrate de que todos los servicios estén en estado `Up` o `Exited (0)` (en el caso de `setup_service`):

    ```bash
    docker compose ps
    ```

3.  **Iniciar la TUI (Interfaz de Consulta):**
    Una vez que las bases de datos estén inicializadas, puedes iniciar la interfaz para ejecutar las *queries*.

    ```bash
    docker compose exec cli python cli.py
    ```

    *Dentro de la TUI, selecciona el ID del script que deseas ejecutar y presiona Enter.*

4.  **Detener y Limpiar:**
    Para detener todos los servicios y eliminar los contenedores y volúmenes (si usaste `-v` en `down`), usa:

    ```bash
    docker compose down -v
    ```
5. **Conectar al servicio:**
    Para conectarte con algun servicio en particular.
    ```bash
    docker exec -it 84c107aef385 bash
    ```

## 🔑 Credenciales (Configuración por Defecto)

| Servicio | Host (Interno) | Usuario | Contraseña | Base de Datos (Inicial) | Puerto (Local) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MySQL** | `mysql` | `root` | `root_password` | `my_data_warehouse` | `3306` |
| **MongoDB** | `mongodb` | `rootuser` | `rootpassword` | `starbucks_transactions` | `27017` |
| **Cassandra** | `cassandra` | (N/A) | (N/A) | `keyspace_starbucks` | `9042` |
| **Neo4j** | `neo4j` | `neo4j` | `neo4jpass` | `neo4j` | `7687` |
| **Redis** | `redis` | (N/A) | (N/A) | (N/A) | `6379` |