-- setup/01_mysql_init.sql

-- ----------------------------------------------------
-- 1. DATABASE AND USER SETUP
-- The Docker Compose already handles the basic DB creation (my_data_warehouse)
-- ----------------------------------------------------
USE my_data_warehouse;

-- ----------------------------------------------------
-- 1.5 Drop tables if exists
-- ----------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS Stock;       -- Siempre empezar por las tablas dependientes (las que tienen FKs hacia otras)
DROP TABLE IF EXISTS Producto;
DROP TABLE IF EXISTS Sucursal;
DROP TABLE IF EXISTS Promocion;
DROP TABLE IF EXISTS Cliente;     -- Y terminar por las tablas principales

SET FOREIGN_KEY_CHECKS = 1;
-- ----------------------------------------------------
-- 2. TABLE CREATION (Core Entities)
-- ----------------------------------------------------

-- Table for main user data
CREATE TABLE IF NOT EXISTS Cliente (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    domicilio VARCHAR(255),
    saldo DECIMAL(10, 2) DEFAULT 0.00,
    stars_acumuladas INT,
    fechaRegistro DATE NOT NULL,
    estadoMembresia VARCHAR(50) NOT NULL
);

-- Table for physical store locations
CREATE TABLE IF NOT EXISTS Sucursal (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pais VARCHAR(50) NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    horario VARCHAR(100),
    capacidad INT
);

-- Table for available products
CREATE TABLE IF NOT EXISTS Producto (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL
);

-- Table for promotions/discounts
CREATE TABLE IF NOT EXISTS Promocion (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    descuento DECIMAL(5, 2) NOT NULL,
    pais VARCHAR(50),
    fechaInicio DATE NOT NULL,
    fechaFin DATE NOT NULL
);

-- Table for managing inventory (Many-to-Many: Sucursal <-> Producto)
CREATE TABLE IF NOT EXISTS Stock (
    id INT PRIMARY KEY AUTO_INCREMENT,
    idSucursal INT NOT NULL,
    idProducto INT NOT NULL,
    cantidad INT NOT NULL,
    FOREIGN KEY (idSucursal) REFERENCES Sucursal(id),
    FOREIGN KEY (idProducto) REFERENCES Producto(id),
    UNIQUE KEY (idSucursal, idProducto) -- Ensure unique stock per product/store
);

-- ----------------------------------------------------
-- 3. INITIAL INSERTS (Seed Data)
-- ----------------------------------------------------
-- Inserta sucursales. Si una sucursal ya existe (ej. por clave primaria), la ignora.
INSERT IGNORE INTO Sucursal (pais, ciudad, direccion, horario, capacidad) VALUES
('USA', 'New York', '123 Main St', '7am-9pm', 50),
('Argentina', 'Buenos Aires', 'Av. Corrientes 456', '8am-8pm', 40),
('Argentina', 'Buenos Aires', 'Av. Del Libertador 69', '8am-8pm', 20);

-- Inserta productos. Si un producto ya existe (ej. por nombre único), lo ignora.
INSERT IGNORE INTO Producto (nombre, tipo, precio) VALUES
('Latte', 'Bebida', 4.50),
('Muffin', 'Comida', 3.00),
('Frappuccino', 'Bebida', 5.50);

-- Inserta un cliente. Si el cliente ya existe (ej. por email único), lo ignora.
INSERT IGNORE INTO Cliente (nombre, email, telefono, domicilio, saldo, stars_acumuladas, fechaRegistro, estadoMembresia) VALUES
('Alice Johnson', 'alice@example.com', '555-1234', '10 Elm St', 15.00, 5, CURDATE(), 'Activo'),
('Jhon Doe', 'john.doe@example.com', '555-1234-5678', '10 Elm St', 150.00, 0, '2000-01-01', 'Inactivo');

-- Inserta una promoción. Si la promoción ya existe, la ignora.
INSERT IGNORE INTO Promocion (nombre, tipo, descuento, pais, fechaInicio, fechaFin) VALUES
('Happy Hour', 'Porcentaje', 0.10, 'USA', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY));

-- Inserta stock. Si la combinación de idSucursal e idProducto ya existe, la ignora.
INSERT IGNORE INTO Stock (idSucursal, idProducto, cantidad) VALUES
(1, 1, 100), (1, 2, 50),
(2, 1, 80), (2, 3, 60);