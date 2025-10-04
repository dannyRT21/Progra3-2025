-- Crear base de datos si no existe

USE db_copyvariedades;

-- Tabla: USUARIOS
CREATE TABLE IF NOT EXISTS usuarios (
    id CHAR(36) PRIMARY KEY,
    nombre CHAR(100) NOT NULL,
    correo_electronico CHAR(100) NOT NULL UNIQUE,
    contrasena CHAR(128) NOT NULL,
    rol CHAR(20) NOT NULL
);

-- Tabla: DIRECCIONES
CREATE TABLE IF NOT EXISTS direcciones (
    id CHAR(36) PRIMARY KEY,
    usuario_id CHAR(36),
    direccion CHAR(255) NOT NULL,
    ciudad CHAR(50) NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla: CATEGORIAS
CREATE TABLE IF NOT EXISTS categorias (
    id CHAR(36) PRIMARY KEY,
    nombre CHAR(50) NOT NULL
);

-- Tabla: PRODUCTOS
CREATE TABLE IF NOT EXISTS productos (
    id CHAR(36) PRIMARY KEY,
    categoria_id CHAR(36),
    nombre CHAR(100) NOT NULL,
    descripcion CHAR(255),
    precio DECIMAL(10,2) NOT NULL,
    cod_barras CHAR(13) NOT NULL UNIQUE,
    inventario INT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- Tabla: COMENTARIOS
CREATE TABLE IF NOT EXISTS comentarios (
    id CHAR(36) PRIMARY KEY,
    nombre CHAR(100) NOT NULL,
    e_mail CHAR(100) NOT NULL,
    asunto CHAR(150) NOT NULL,
    comentario TEXT NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
