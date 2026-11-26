-- Base de datos de ventas (sintética) de un centro de psicología online · SQLite
DROP TABLE IF EXISTS sesiones;
DROP TABLE IF EXISTS pacientes;
DROP TABLE IF EXISTS canales;

CREATE TABLE canales (
    id_canal INTEGER PRIMARY KEY,
    nombre   TEXT NOT NULL UNIQUE,
    tipo     TEXT NOT NULL
);

CREATE TABLE pacientes (
    id_paciente          TEXT PRIMARY KEY,
    id_canal             INTEGER NOT NULL REFERENCES canales(id_canal),
    fecha_primera_sesion TEXT NOT NULL,
    plan                 TEXT NOT NULL,
    tipo_terapia         TEXT NOT NULL
);

CREATE TABLE sesiones (
    id_sesion   TEXT PRIMARY KEY,
    id_paciente TEXT NOT NULL REFERENCES pacientes(id_paciente),
    fecha       TEXT NOT NULL,
    monto       REAL NOT NULL CHECK (monto > 0)
);
