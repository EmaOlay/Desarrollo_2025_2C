#!/bin/bash
clear
set -e # Exit immediately if a command exits with a non-zero status

echo "------------ Starting Database Setup Service ----------------"

# ----------------------------------------
# 1. Wait for all Core Services to be Healthy
# ----------------------------------------

# Wait for MySQL (Port 3306)
/usr/local/bin/wait-for-it.sh mysql:3306 --timeout=60 -- echo "MySQL is up!"

# Wait for MongoDB (Port 27017)
/usr/local/bin/wait-for-it.sh mongodb:27017 --timeout=60 -- echo "MongoDB is up!"

# Wait for Cassandra (Port 9042)
/usr/local/bin/wait-for-it.sh cassandra:9042 --timeout=60 -- echo "Cassandra is up!"

# Wait for Neo4j (Bolt Port 7687)
/usr/local/bin/wait-for-it.sh neo4j:7687 --timeout=60 -- echo "Neo4j is up!"

# Wait for Redis (Port 6379)
/usr/local/bin/wait-for-it.sh redis:6379 --timeout=30 -- echo "Redis is up!"

echo "--- All core databases are running. Starting initialization scripts. ---"

# ----------------------------------------
# 2. Execute Setup Scripts (using client tools)
# ----------------------------------------

# NOTE: The actual commands below require the corresponding client tools (mysql, mongo, cqlsh, cypher-shell)
# to be installed in the Dockerfile above. Assuming they are available.

# MySQL Setup
echo "Running MySQL setup..."
mysql -h mysql -u root -proot_password my_data_warehouse < /setup_scripts/01_mysql_init.sql
echo "MySQL setup finished"
# MongoDB Setup
echo "Running MongoDB setup..."
MONGO_USER="rootuser" 
MONGO_PASS="rootpassword"

# Usamos la base de datos 'admin' para la autenticación y luego especificamos la DB de trabajo.
mongosh mongodb://mongodb:27017/starbucks_transactions \
    -u "$MONGO_USER" \
    -p "$MONGO_PASS" \
    --authenticationDatabase "admin" \
    --file /setup_scripts/02_mongodb_init.js
echo "MongoDB setup finished"
# Cassandra Setup
echo "Running Cassandra setup..."
# Use cqlsh to execute the script
cqlsh -f /setup_scripts/03_cassandra_init.cql cassandra 9042
echo "Cassandra setup finished"
# Neo4j Setup
# Variables de conexión
NEO4J_URI="bolt://neo4j:7687"
NEO4J_USER="neo4j"
NEO4J_PASS="neo4jpassword"
NEO4J_DB_NAME="neo4j"

echo "Running Neo4j setup..."

# 2. Inicializar la base de datos 'mydata'
echo "Initializing data in ${NEO4J_DB_NAME}..."
cat /setup_scripts/04_neo4j_init.cypher | cypher-shell -a "${NEO4J_URI}" -u "${NEO4J_USER}" -p "${NEO4J_PASS}" --database "${NEO4J_DB_NAME}"

echo "Neo4j setup finished"

# Redis Configuration (Optional: Apply configuration via CLI if needed, otherwise skip)
echo "Redis configuration applied via Docker Compose command (or skipped)."

echo "----------- All database setups are complete! ----------------"