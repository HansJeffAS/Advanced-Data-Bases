from __future__ import annotations

import psycopg

from config import load_config

DDL = (
    "DROP TRIGGER IF EXISTS alumnos_audit ON alumnos;",
    "DROP TRIGGER IF EXISTS profesores_audit ON profesores;",
    "DROP TRIGGER IF EXISTS asignaturas_audit ON asignaturas;",
    "DROP TRIGGER IF EXISTS matriculas_audit ON matriculas;",
    "DROP FUNCTION IF EXISTS process_alumnos_audit, process_profesores_audit, process_asignatura_audit, process_matriculas_audit;",
    "DROP FUNCTION IF EXISTS matricular_alumno;",
    """
    CREATE OR REPLACE FUNCTION process_alumnos_audit() RETURNS TRIGGER AS $alumnos_audit$
        BEGIN
            IF (TG_OP = 'DELETE') THEN
                INSERT INTO alumnos_audit (operation, stamp, userid, alumno_id, nombre, email_alumno, saldo)
                VALUES ('D', now(), current_user, OLD.alumno_id, OLD.nombre, OLD.email_alumno, OLD.saldo);
            ELSIF (TG_OP = 'UPDATE') THEN
                INSERT INTO alumnos_audit (operation, stamp, userid, alumno_id, nombre, email_alumno, saldo)
                VALUES ('U', now(), current_user, NEW.alumno_id, NEW.nombre, NEW.email_alumno, NEW.saldo);
            ELSIF (TG_OP = 'INSERT') THEN
                INSERT INTO alumnos_audit (operation, stamp, userid, alumno_id, nombre, email_alumno, saldo)
                VALUES ('I', now(), current_user, NEW.alumno_id, NEW.nombre, NEW.email_alumno, NEW.saldo);
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
                INSERT INTO asignaturas_audit (operation, stamp, userid, asignatura_id, profesor_id, nombre, precio, max_alumnos)
                VALUES ('D', now(), current_user, OLD.asignatura_id, OLD.profesor_id, OLD.nombre, OLD.precio, OLD.max_alumnos);
            ELSIF (TG_OP = 'UPDATE') THEN
                INSERT INTO asignaturas_audit (operation, stamp, userid, asignatura_id, profesor_id, nombre, precio, max_alumnos)
                VALUES ('U', now(), current_user, NEW.asignatura_id, NEW.profesor_id, NEW.nombre, NEW.precio, NEW.max_alumnos);
            ELSIF (TG_OP = 'INSERT') THEN
                INSERT INTO asignaturas_audit (operation, stamp, userid, asignatura_id, profesor_id, nombre, precio, max_alumnos)
                VALUES ('I', now(), current_user, NEW.asignatura_id, NEW.profesor_id, NEW.nombre, NEW.precio, NEW.max_alumnos);
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
    """,
    """
    CREATE OR REPLACE FUNCTION matricular_alumno(
        p_alumno_id     INTEGER,
        p_asignatura_id INTEGER
    ) RETURNS JSONB AS $$
    DECLARE
        v_alumno        alumnos%ROWTYPE;
        v_asignatura    asignaturas%ROWTYPE;
        v_inscritos     INTEGER;
        v_ya_matriculado INTEGER;
    BEGIN
        -- Bloqueamos la fila del alumno para evitar condiciones de carrera
        SELECT * INTO v_alumno
        FROM alumnos
        WHERE alumno_id = p_alumno_id
        FOR UPDATE;

        IF NOT FOUND THEN
            RETURN jsonb_build_object('ok', false, 'error', 'Alumno no encontrado');
        END IF;

        -- Bloqueamos la fila de la asignatura
        SELECT * INTO v_asignatura
        FROM asignaturas
        WHERE asignatura_id = p_asignatura_id
        FOR UPDATE;

        IF NOT FOUND THEN
            RETURN jsonb_build_object('ok', false, 'error', 'Asignatura no encontrada');
        END IF;

        -- Verificamos si el alumno ya está matriculado en esta asignatura
        SELECT COUNT(*) INTO v_ya_matriculado
        FROM matriculas
        WHERE alumno_id = p_alumno_id AND asignatura_id = p_asignatura_id;

        IF v_ya_matriculado > 0 THEN
            RETURN jsonb_build_object('ok', false, 'error', 'El alumno ya está matriculado en esta asignatura');
        END IF;

        -- Contamos los alumnos ya inscritos en la asignatura
        SELECT COUNT(*) INTO v_inscritos
        FROM matriculas
        WHERE asignatura_id = p_asignatura_id;

        -- Verificamos que quedan plazas disponibles
        IF v_inscritos >= v_asignatura.max_alumnos THEN
            RETURN jsonb_build_object(
                'ok', false,
                'error', 'No quedan plazas disponibles (límite: ' || v_asignatura.max_alumnos || ')'
            );
        END IF;

        -- Verificamos que el alumno tiene saldo suficiente
        IF v_alumno.saldo < v_asignatura.precio THEN
            RETURN jsonb_build_object(
                'ok', false,
                'error', 'Saldo insuficiente (tienes ' || v_alumno.saldo || '€, necesitas ' || v_asignatura.precio || '€)'
            );
        END IF;

        -- Descontamos el precio del saldo del alumno
        UPDATE alumnos
        SET saldo = saldo - v_asignatura.precio
        WHERE alumno_id = p_alumno_id;

        -- Insertamos la matrícula
        INSERT INTO matriculas (alumno_id, asignatura_id)
        VALUES (p_alumno_id, p_asignatura_id);

        RETURN jsonb_build_object(
            'ok', true,
            'mensaje', 'Matrícula realizada con éxito',
            'alumno', v_alumno.nombre,
            'asignatura', v_asignatura.nombre,
            'precio', v_asignatura.precio,
            'saldo_restante', v_alumno.saldo - v_asignatura.precio,
            'plazas_restantes', v_asignatura.max_alumnos - v_inscritos - 1
        );

    EXCEPTION
        WHEN OTHERS THEN
            RETURN jsonb_build_object('ok', false, 'error', 'Error interno: ' || SQLERRM);
    END;
    $$ LANGUAGE plpgsql;
    """
)

def create_functions() -> None:
    cfg = load_config()
    try:
        with psycopg.connect(**cfg) as conn:
            with conn.cursor() as cur:
                for stmt in DDL:
                    cur.execute(stmt)
                conn.commit() 
        print("Funciones creadas (Drop + Create).")
    except Exception as e:
        print(f"Error al crear la funcion: {e}")

if __name__ == "__main__":
    create_functions()