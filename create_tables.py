from __future__ import annotations

import psycopg

from config import load_config

DDL = (
    "CREATE EXTENSION IF NOT EXISTS unaccent;",
    "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
    "CREATE EXTENSION IF NOT EXISTS postgis;",
    "DROP TABLE IF EXISTS matriculas, alumnos, asignaturas, profesores, alumnos_audit, profesores_audit, asignaturas_audit, matriculas_audit CASCADE;", 
    """
    CREATE TABLE alumnos (
        alumno_id SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email_alumno VARCHAR(255) NOT NULL,
        saldo NUMERIC(10,2) DEFAULT 0.00 NOT NULL,
        ubicacion GEOMETRY(Point, 4326)
    )
    """,
    """
    CREATE TABLE profesores (
        profesor_id SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email_profesor VARCHAR(255) NOT NULL
    )
    """,
    """
    CREATE TABLE asignaturas (
        asignatura_id SERIAL PRIMARY KEY,
        profesor_id INTEGER REFERENCES profesores(profesor_id) ON DELETE SET NULL,
        nombre JSONB NOT NULL,
        precio NUMERIC(10,2) DEFAULT 0.00 NOT NULL,
        max_alumnos INTEGER DEFAULT 30 NOT NULL,
        area GEOMETRY(Polygon, 4326)
    )
    """,
    """
    CREATE TABLE matriculas (
        matricula_id SERIAL PRIMARY KEY,
        asignatura_id INTEGER REFERENCES asignaturas(asignatura_id) ON DELETE CASCADE,
        alumno_id INTEGER REFERENCES alumnos(alumno_id) ON DELETE CASCADE,
        fecha_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE alumnos_audit (
        audit_id SERIAL PRIMARY KEY,
        operation char(1) NOT NULL,
        stamp timestamp NOT NULL,
        userid text NOT NULL,
        alumno_id integer,
        nombre text NOT NULL,
        email_alumno text NOT NULL,
        saldo numeric(10,2),
        ubicacion GEOMETRY(Point, 4326)
    )
    """,
    """
    CREATE TABLE profesores_audit (
        audit_id SERIAL PRIMARY KEY,
        operation char(1) NOT NULL,
        stamp timestamp NOT NULL,
        userid text NOT NULL,
        profesor_id integer,
        nombre text NOT NULL,
        email_profesor text NOT NULL
    )
    """,
    """
    CREATE TABLE asignaturas_audit (
        audit_id SERIAL PRIMARY KEY,
        operation char(1) NOT NULL,
        stamp timestamp NOT NULL,
        userid text NOT NULL,
        asignatura_id integer,
        profesor_id integer,
        nombre JSONB NOT NULL,
        precio numeric(10,2),
        max_alumnos integer,
        area GEOMETRY(Polygon, 4326)
    )
    """,
    """
    CREATE TABLE matriculas_audit (
        audit_id SERIAL PRIMARY KEY,
        operation char(1) NOT NULL,
        stamp timestamp NOT NULL,
        userid text NOT NULL,    
        matricula_id integer,
        asignatura_id integer,
        alumno_id integer,
        fecha_matricula timestamp
    )
    """,
    "DROP VIEW IF EXISTS vista_matriculas_detalle;",
    """
    CREATE VIEW vista_matriculas_detalle AS
    SELECT
        al.nombre        AS nombre_alumno,
        pr.nombre        AS nombre_profesor,
        (asig.nombre->>'es') || ' (' || (asig.nombre->>'en') || ')' AS nombre_asignatura
    FROM matriculas m
    JOIN alumnos      al   ON al.alumno_id       = m.alumno_id
    JOIN asignaturas  asig ON asig.asignatura_id = m.asignatura_id
    LEFT JOIN profesores pr ON pr.profesor_id    = asig.profesor_id
    ORDER BY al.nombre, asig.nombre;
    """,

    # Índices B-tree
    "CREATE INDEX IF NOT EXISTS idx_alumnos_saldo              ON alumnos(saldo);",

    "CREATE INDEX IF NOT EXISTS idx_asignaturas_profesor_id    ON asignaturas(profesor_id);",
    "CREATE INDEX IF NOT EXISTS idx_asignaturas_precio         ON asignaturas(precio);",
    "CREATE INDEX IF NOT EXISTS idx_asignaturas_max_alumnos    ON asignaturas(max_alumnos);",

    "CREATE INDEX IF NOT EXISTS idx_matriculas_alumno_id       ON matriculas(alumno_id);",
    "CREATE INDEX IF NOT EXISTS idx_matriculas_asignatura_id   ON matriculas(asignatura_id);",
    "CREATE INDEX IF NOT EXISTS idx_matriculas_fecha_matricula ON matriculas(fecha_matricula);",

    "CREATE INDEX IF NOT EXISTS idx_alumnos_audit_stamp        ON alumnos_audit(stamp);",
    "CREATE INDEX IF NOT EXISTS idx_alumnos_audit_operation    ON alumnos_audit(operation);",
    "CREATE INDEX IF NOT EXISTS idx_profesores_audit_stamp     ON profesores_audit(stamp);",
    "CREATE INDEX IF NOT EXISTS idx_profesores_audit_operation ON profesores_audit(operation);",
    "CREATE INDEX IF NOT EXISTS idx_asignaturas_audit_stamp    ON asignaturas_audit(stamp);",
    "CREATE INDEX IF NOT EXISTS idx_asignaturas_audit_operation ON asignaturas_audit(operation);",

    # Índices GIN con pg_trgm
    "CREATE INDEX IF NOT EXISTS idx_gin_alumnos_nombre         ON alumnos         USING GIN(nombre          gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS idx_gin_alumnos_email          ON alumnos         USING GIN(email_alumno    gin_trgm_ops);",

    "CREATE INDEX IF NOT EXISTS idx_gin_profesores_nombre      ON profesores      USING GIN(nombre          gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS idx_gin_profesores_email       ON profesores      USING GIN(email_profesor  gin_trgm_ops);",

    "CREATE INDEX IF NOT EXISTS idx_gin_asignaturas_nombre_jsonb ON asignaturas USING GIN(nombre jsonb_path_ops);",
    "CREATE INDEX IF NOT EXISTS idx_fts_asignaturas_nombre_es ON asignaturas USING GIN(to_tsvector('spanish', nombre->>'es'));",
    "CREATE INDEX IF NOT EXISTS idx_fts_asignaturas_nombre_en ON asignaturas USING GIN(to_tsvector('english', nombre->>'en'));",
    "CREATE INDEX IF NOT EXISTS idx_trgm_asignaturas_nombre_es ON asignaturas USING GIN((nombre->>'es') gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS idx_trgm_asignaturas_nombre_en ON asignaturas USING GIN((nombre->>'en') gin_trgm_ops);",

    "CREATE INDEX IF NOT EXISTS idx_gin_alumnos_audit_nombre   ON alumnos_audit   USING GIN(nombre          gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS idx_gin_alumnos_audit_email    ON alumnos_audit   USING GIN(email_alumno    gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS idx_gin_profesores_audit_nombre ON profesores_audit USING GIN(nombre        gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS idx_gin_profesores_audit_email  ON profesores_audit USING GIN(email_profesor gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS idx_gin_asignaturas_audit_nombre_jsonb ON asignaturas_audit USING GIN(nombre jsonb_path_ops);",
    "CREATE INDEX IF NOT EXISTS idx_fts_asignaturas_audit_nombre_es ON asignaturas_audit USING GIN(to_tsvector('spanish', nombre->>'es'));",
    "CREATE INDEX IF NOT EXISTS idx_fts_asignaturas_audit_nombre_en ON asignaturas_audit USING GIN(to_tsvector('english', nombre->>'en'));",
    "CREATE INDEX IF NOT EXISTS idx_trgm_asignaturas_audit_nombre_es ON asignaturas_audit USING GIN((nombre->>'es') gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS idx_trgm_asignaturas_audit_nombre_en ON asignaturas_audit USING GIN((nombre->>'en') gin_trgm_ops);",

    # Índices GiST espaciales (Optimizaciones Críticas PostGIS)
    "CREATE INDEX IF NOT EXISTS idx_gist_alumnos_ubicacion     ON alumnos          USING GIST(ubicacion);",
    "CREATE INDEX IF NOT EXISTS idx_gist_asignaturas_area      ON asignaturas      USING GIST(area);"
)

def create_tables() -> None:
    cfg = load_config()
    try:
        with psycopg.connect(**cfg) as conn:
            with conn.cursor() as cur:
                for stmt in DDL:
                    cur.execute(stmt)
                conn.commit() 
        print("Tablas, vista e índices reiniciados correctamente (Drop + Create).")
    except Exception as e:
        print(f"Error al procesar la base de datos: {e}")

if __name__ == "__main__":
    create_tables()