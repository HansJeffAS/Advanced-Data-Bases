from __future__ import annotations

import psycopg

from config import load_config

# Añadimos el DROP al inicio de la secuencia de comandos
DDL = (
    "DROP TRIGGER IF EXISTS alumnos_audit ON alumnos;",
    "DROP TRIGGER IF EXISTS profesores_audit ON profesores;",
    "DROP TRIGGER IF EXISTS asignaturas_audit ON asignaturas;",
    "DROP TRIGGER IF EXISTS matriculas_audit ON matriculas;",
    "DROP FUNCTION IF EXISTS process_alumnos_audit, process_profesores_audit, process_asignatura_audit, process_matriculas_audit;",
    """
    CREATE OR REPLACE FUNCTION process_alumnos_audit() RETURNS TRIGGER AS $alumnos_audit$
        BEGIN
            IF (TG_OP = 'DELETE') THEN
                INSERT INTO alumnos_audit (operation, stamp, userid, alumno_id, nombre, email_alumno, dinero)
                VALUES ('D', now(), current_user, OLD.alumno_id, OLD.nombre, OLD.email_alumno, OLD.dinero);
            ELSIF (TG_OP = 'UPDATE') THEN
                INSERT INTO alumnos_audit (operation, stamp, userid, alumno_id, nombre, email_alumno, dinero)
                VALUES ('U', now(), current_user, NEW.alumno_id, NEW.nombre, NEW.email_alumno, NEW.dinero);
            ELSIF (TG_OP = 'INSERT') THEN
                INSERT INTO alumnos_audit (operation, stamp, userid, alumno_id, nombre, email_alumno, dinero)
                VALUES ('I', now(), current_user, NEW.alumno_id, NEW.nombre, NEW.email_alumno, NEW.dinero);
            END IF;
            RETURN NULL; -- result is ignored since this is an AFTER trigger
        END;
    $alumnos_audit$ LANGUAGE plpgsql;
    """,
    """
    CREATE OR REPLACE FUNCTION process_profesores_audit() RETURNS TRIGGER AS $profesores_audit$
        BEGIN
            IF (TG_OP = 'DELETE') THEN
                INSERT INTO profesores_audit (operation, stamp, userid, profesor_id, nombre, email_profesor)
                VALUES ('D', now(), current_user, OLD.profesor_id, OLD.nombre, OLD.email_profesor);
            ELSIF (TG_OP = 'UPDATE') THEN
                INSERT INTO profesores_audit (operation, stamp, userid, profesor_id, nombre, email_profesor)
                VALUES ('U', now(), current_user, NEW.profesor_id, NEW.nombre, NEW.email_profesor);
            ELSIF (TG_OP = 'INSERT') THEN
                INSERT INTO profesores_audit (operation, stamp, userid, profesor_id, nombre, email_profesor)
                VALUES ('I', now(), current_user, NEW.profesor_id, NEW.nombre, NEW.email_profesor);
            END IF;
            RETURN NULL;
        END;
    $profesores_audit$ LANGUAGE plpgsql;
    """,
    """
    CREATE OR REPLACE FUNCTION process_asignatura_audit() RETURNS TRIGGER AS $asignaturas_audit$
        BEGIN
            IF (TG_OP = 'DELETE') THEN
                INSERT INTO asignaturas_audit (operation, stamp, userid, asignatura_id, profesor_id, nombre, costo, cupo_maximo)
                VALUES ('D', now(), current_user, OLD.asignatura_id, OLD.profesor_id, OLD.nombre, OLD.costo, OLD.cupo_maximo);
            ELSIF (TG_OP = 'UPDATE') THEN
                INSERT INTO asignaturas_audit (operation, stamp, userid, asignatura_id, profesor_id, nombre, costo, cupo_maximo)
                VALUES ('U', now(), current_user, NEW.asignatura_id, NEW.profesor_id, NEW.nombre, NEW.costo, NEW.cupo_maximo);
            ELSIF (TG_OP = 'INSERT') THEN
                INSERT INTO asignaturas_audit (operation, stamp, userid, asignatura_id, profesor_id, nombre, costo, cupo_maximo)
                VALUES ('I', now(), current_user, NEW.asignatura_id, NEW.profesor_id, NEW.nombre, NEW.costo, NEW.cupo_maximo);
            END IF;
            RETURN NULL;
        END;
    $asignaturas_audit$ LANGUAGE plpgsql;
    """,
    """
    CREATE OR REPLACE FUNCTION process_matriculas_audit() RETURNS TRIGGER AS $matriculas_audit$
        BEGIN
            IF (TG_OP = 'DELETE') THEN
                INSERT INTO matriculas_audit (operation, stamp, userid, matricula_id, alumno_id, asignatura_id, fecha_matricula)
                VALUES ('D', now(), current_user, OLD.matricula_id, OLD.alumno_id, OLD.asignatura_id, OLD.fecha_matricula);
            ELSIF (TG_OP = 'UPDATE') THEN
                INSERT INTO matriculas_audit (operation, stamp, userid, matricula_id, alumno_id, asignatura_id, fecha_matricula)
                VALUES ('U', now(), current_user, NEW.matricula_id, NEW.alumno_id, NEW.asignatura_id, NEW.fecha_matricula);
            ELSIF (TG_OP = 'INSERT') THEN
                INSERT INTO matriculas_audit (operation, stamp, userid, matricula_id, alumno_id, asignatura_id, fecha_matricula)
                VALUES ('I', now(), current_user, NEW.matricula_id, NEW.alumno_id, NEW.asignatura_id, NEW.fecha_matricula);
            END IF;
            RETURN NULL;
        END;
    $matriculas_audit$ LANGUAGE plpgsql;
    """,
    """
    CREATE TRIGGER alumnos_audit
    AFTER INSERT OR UPDATE OR DELETE ON alumnos
        FOR EACH ROW EXECUTE FUNCTION process_alumnos_audit();
    """,
    """
    CREATE TRIGGER profesores_audit
    AFTER INSERT OR UPDATE OR DELETE ON profesores
        FOR EACH ROW EXECUTE FUNCTION process_profesores_audit();
    """,
    """
    CREATE TRIGGER asignaturas_audit
    AFTER INSERT OR UPDATE OR DELETE ON asignaturas
        FOR EACH ROW EXECUTE FUNCTION process_asignatura_audit();
    """,
    """
    CREATE TRIGGER matriculas_audit
    AFTER INSERT OR UPDATE OR DELETE ON matriculas
        FOR EACH ROW EXECUTE FUNCTION process_matriculas_audit();
    """
)

def create_functions() -> None:
    cfg = load_config()
    try:
        with psycopg.connect(**cfg) as conn:
            with conn.cursor() as cur:
                for stmt in DDL:
                    cur.execute(stmt)
                # Es buena práctica hacer commit explícito si no usas autocommit
                conn.commit() 
        print("Funciones creadas (Drop + Create).")
    except Exception as e:
        print(f"Error al crear la funcion: {e}")

if __name__ == "__main__":
    create_functions()