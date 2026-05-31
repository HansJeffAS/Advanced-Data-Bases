from __future__ import annotations

import psycopg

from config import load_config

DDL = (
    "DROP TABLE IF EXISTS matriculas, alumnos, asignaturas, profesores, alumnos_audit, profesores_audit, asignaturas_audit, matriculas_audit CASCADE;", 
    """
    CREATE TABLE alumnos (
        alumno_id SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email_alumno VARCHAR(255) NOT NULL,
        saldo NUMERIC(10,2) DEFAULT 0.00 NOT NULL
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
        nombre VARCHAR(100) NOT NULL,
        precio NUMERIC(10,2) DEFAULT 0.00 NOT NULL,
        max_alumnos INTEGER DEFAULT 30 NOT NULL
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
        saldo numeric(10,2)
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
        nombre text NOT NULL,
        precio numeric(10,2),
        max_alumnos integer
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
    """
)

def create_tables() -> None:
    cfg = load_config()
    try:
        with psycopg.connect(**cfg) as conn:
            with conn.cursor() as cur:
                for stmt in DDL:
                    cur.execute(stmt)
                conn.commit() 
        print("Tablas reiniciadas correctamente (Drop + Create).")
    except Exception as e:
        print(f"Error al procesar la base de datos: {e}")

if __name__ == "__main__":
    create_tables()