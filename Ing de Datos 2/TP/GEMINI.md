# GEMINI.md - Project Overview

This document provides a comprehensive overview of the "TP Ingeniería de Datos II: Starbucks Políglota" project, designed to serve as instructional context for future interactions.

## Project Overview

This project implements a polyglot data architecture to simulate the information systems of a Starbucks-like coffee chain. The core idea is to leverage the most suitable database technology for each data type and business requirement, encompassing catalog management, transactional data, loyalty information, and relational analytics.

The entire system is orchestrated using **Docker Compose**, and a **Text User Interface (TUI)**, built with Python and the `rich` library, is provided to demonstrate the functionality of various queries across different database engines.

**Key Technologies and Architecture:**

The project utilizes a polyglot persistence approach with the following services:

*   **MySQL:** Used for master and relational data, ensuring transactional integrity (ACID) and a rigid schema for entities like `Producto`, `Sucursal`, and `Cliente`, as well as loyalty data.
*   **MongoDB:** Employed for transactional and document-oriented data, storing detailed purchase orders and historical transactions.
*   **Apache Cassandra:** Ideal for analytical and time-series data, recording purchase history (`HistorialCompra`) and system logs due to its high write frequency capabilities.
*   **Neo4j:** A graph database for analyzing complex relationships, such as "most connected products" or customer recommendation networks.
*   **Redis:** Functions as a caching layer for volatile data like user sessions or cached menus, enhancing performance.
*   **CLI (Python with Rich):** A TUI for executing and demonstrating business queries across all integrated databases.
*   **Setup Service:** A dedicated service responsible for initializing all databases and injecting initial data and schema structures.

## Building and Running the Project

The project is designed to be built and run using Docker Compose.

### Prerequisites

*   Docker (v20.10.0+)
*   Docker Compose (v2.0.0+)

### Execution Steps

1.  **Build and Launch Containers:**
    This command builds the `cli` image and brings up all services, including the `setup_service` which initializes the databases.

    ```bash
    docker compose up --build
    ```

2.  **Verify Service Status:**
    Ensure all services are in an `Up` state. The `setup_service` will likely show `Exited (0)` once its initialization tasks are complete.

    ```bash
    docker compose ps
    ```

3.  **Start the TUI (Query Interface):**
    Once the databases are initialized and running, you can access the interactive TUI to execute queries.

    ```bash
    docker compose exec cli python cli_v2.py
    ```
    *Inside the TUI, you can navigate through directories to find and execute specific scripts by entering their corresponding ID.*

4.  **Stop and Clean Up:**
    To stop all services and remove containers and volumes (if `-v` is used), execute:

    ```bash
    docker compose down -v
    ```

## Development Conventions

*   **Polyglot Architecture:** The project strictly adheres to a polyglot persistence model, selecting specific database technologies based on the nature and access patterns of the data.
*   **Query Organization:** All database interaction scripts and queries are organized within the `queries/` directory, categorized by their purpose (e.g., `Casos_de_Uso/`, `Pruebas/`) and often by database technology.
*   **CLI for Interaction:** The primary method for interacting with and demonstrating the database queries is through the Python-based TUI (`cli/cli_v2.py`).
*   **Script Execution:**
    *   Python scripts (`.py`) are executed directly.
    *   SQL scripts (`.sql`) are run against MySQL using the `mysql` client.
    *   MongoDB scripts (`.js`) are executed via `mongosh`.
    *   Cassandra scripts (`.cql`) are executed using `cqlsh`.
    *   Neo4j scripts (`.cypher`) are handled by a dedicated Python function within `cli_v2.py` that uses the `neo4j` driver.
*   **Authentication and Session Management:** The CLI incorporates a basic authentication and session management system using Redis, where user passwords are hashed for storage.
*   **Database Credentials:** Default credentials for all databases are defined in `docker-compose.yml` and documented in the `README.md`.
