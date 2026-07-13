-- ==========================================
-- PROYECTO PÚLSAR: ESQUEMA BASE DE EL NÚCLEO
-- Motor: PostgreSQL
-- ==========================================

-- 1. Tabla de Usuarios (B2C Jugadores y B2B Desarrolladores)
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    correo VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    tipo_cuenta VARCHAR(20) CHECK (tipo_cuenta IN ('jugador', 'desarrollador')) NOT NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP WITH TIME ZONE
);

-- 2. Tabla del Catálogo Base de Juegos
-- Solo datos duros y consistentes. Los metadatos y etiquetas irán a La Nebulosa.
CREATE TABLE juegos_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    desarrollador_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    titulo VARCHAR(150) NOT NULL,
    plataforma_base VARCHAR(100) NOT NULL,
    fecha_lanzamiento DATE,
    fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar futuras búsquedas desde El Pulso
CREATE INDEX idx_usuarios_correo ON usuarios(correo);
CREATE INDEX idx_juegos_titulo ON juegos_base(titulo);
CREATE INDEX idx_juegos_desarrollador ON juegos_base(desarrollador_id);