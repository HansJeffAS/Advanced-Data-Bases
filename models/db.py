from __future__ import annotations

import psycopg
from psycopg import sql
import json

from config import load_config

from datetime import date
from decimal import Decimal
from typing import TypeVar, Type, Any

from models.entities import Alumnos, Profesores, Asignaturas, Matriculas, AlumnosAudit, ProfesoresAudit, AsignaturasAudit


def get_connection():
    """
    Devuelve una conexión a PostgreSQL.

    Usa database.ini vía load_config(). La conexión debe usarse con
    context manager (with ... as conn) para cerrar correctamente.
    """
    cfg = load_config()
    return psycopg.connect(**cfg)

def get_alumnos() -> list[Alumnos]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT alumno_id, nombre, email_alumno, saldo FROM alumnos ORDER BY alumno_id;"
            )
            return [Alumnos(alumno_id=r[0], nombre=r[1], email_alumno=r[2], saldo=r[3]) for r in cur.fetchall()]

def get_profesores() -> list[Profesores]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT profesor_id, nombre, email_profesor FROM profesores ORDER BY profesor_id;"
            )
            return [Profesores(profesor_id=r[0], nombre=r[1], email_profesor=r[2]) for r in cur.fetchall()]
        
def get_asignaturas() -> list[Asignaturas]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT asignatura_id, nombre, profesor_id, precio, max_alumnos FROM asignaturas ORDER BY asignatura_id;"
            )
            return [Asignaturas(asignatura_id=r[0], nombre=r[1], profesor_id=r[2], precio=r[3], max_alumnos=r[4]) for r in cur.fetchall()]
        
def get_matriculas() -> list[Matriculas]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT matricula_id, alumno_id, asignatura_id, fecha_matricula FROM matriculas ORDER BY matricula_id;"
            )
            return [Matriculas(matricula_id=r[0], alumno_id=r[1], asignatura_id=r[2], fecha_matricula=r[3]) for r in cur.fetchall()]

T = TypeVar("T")

def get_auditoria_general(tabla: str, modelo: Type[T]) -> list[T]:
    """
    Obtiene registros de auditoría de cualquier tabla.
    """
    TABLAS_PERMITIDAS = {"alumnos_audit", "profesores_audit", "asignaturas_audit"}

    if tabla not in TABLAS_PERMITIDAS:
        raise ValueError(f"Tabla no permitida: {tabla}")

    with get_connection() as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT * FROM {} ORDER BY stamp DESC;").format(
                sql.Identifier(tabla)
            )
            cur.execute(query)
            return [modelo(*r) for r in cur.fetchall()]
        
def get_auditoria_alumno(alumno: str) -> list[AlumnosAudit]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT audit_id, operation, stamp, userid, alumno_id, nombre, email_alumno, saldo
                FROM alumnos_audit 
                WHERE alumno_id = %s
                ORDER BY stamp DESC;
            """
            try:
                cur.execute(query, (int(alumno),))
            except ValueError:
                return []
            
            return [
                AlumnosAudit(
                    audit_id=r[0], operation=r[1], stamp=r[2], 
                    userid=r[3], alumno_id=r[4], nombre=r[5], email_alumno=r[6], saldo=r[7]
                ) for r in cur.fetchall()
            ]

def get_auditoria_profesor(profesor: str) -> list[ProfesoresAudit]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT audit_id, operation, stamp, userid, profesor_id, nombre, email_profesor 
                FROM profesores_audit 
                WHERE profesor_id = %s
                ORDER BY stamp DESC;
            """
            try:
                cur.execute(query, (int(profesor),))
            except ValueError:
                return []
            
            return [
                ProfesoresAudit(
                    audit_id=r[0], operation=r[1], stamp=r[2], 
                    userid=r[3], profesor_id=r[4], nombre=r[5], email_profesor=r[6]
                ) for r in cur.fetchall()
            ]
        
def get_auditoria_asignatura(asignatura: str) -> list[AsignaturasAudit]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT audit_id, operation, stamp, userid, asignatura_id, profesor_id, nombre, precio, max_alumnos
                FROM asignaturas_audit 
                WHERE asignatura_id = %s
                ORDER BY stamp DESC;
            """
            try:
                cur.execute(query, (int(asignatura),))
            except ValueError:
                return []
            
            return [
                AsignaturasAudit(
                    audit_id=r[0], operation=r[1], stamp=r[2], 
                    userid=r[3], asignatura_id=r[4], profesor_id=r[5], nombre=r[6],
                    precio=r[7], max_alumnos=r[8]
                ) for r in cur.fetchall()
            ]

def get_alumno(alumno_id: int) -> Alumnos | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT alumno_id, nombre, email_alumno, saldo FROM alumnos WHERE alumno_id = %s", (alumno_id,))
            r = cur.fetchone()
            if r:
                return Alumnos(alumno_id=r[0], nombre=r[1], email_alumno=r[2], saldo=r[3])
            return None

def insert_alumno(nombre: str, email_alumno: str, saldo: float = 0.0) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO alumnos (nombre, email_alumno, saldo) VALUES (%s, %s, %s)", (nombre, email_alumno, saldo))
        conn.commit()

def update_alumno(alumno_id: int, nombre: str, email_alumno: str, saldo: float) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE alumnos SET nombre = %s, email_alumno = %s, saldo = %s WHERE alumno_id = %s", (nombre, email_alumno, saldo, alumno_id))
        conn.commit()

def delete_alumno(alumno_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM alumnos WHERE alumno_id = %s", (alumno_id,))
        conn.commit()

def get_profesor(profesor_id: int) -> Profesores | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT profesor_id, nombre, email_profesor FROM profesores WHERE profesor_id = %s", (profesor_id,))
            r = cur.fetchone()
            if r:
                return Profesores(profesor_id=r[0], nombre=r[1], email_profesor=r[2])
            return None

def insert_profesor(nombre: str, email_profesor: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO profesores (nombre, email_profesor) VALUES (%s, %s)", (nombre, email_profesor))
        conn.commit()

def update_profesor(profesor_id: int, nombre: str, email_profesor: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE profesores SET nombre = %s, email_profesor = %s WHERE profesor_id = %s", (nombre, email_profesor, profesor_id))
        conn.commit()

def delete_profesor(profesor_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM profesores WHERE profesor_id = %s", (profesor_id,))
        conn.commit()

def get_asignatura(asignatura_id: int) -> Asignaturas | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT asignatura_id, nombre, profesor_id, precio, max_alumnos FROM asignaturas WHERE asignatura_id = %s", (asignatura_id,))
            r = cur.fetchone()
            if r:
                return Asignaturas(asignatura_id=r[0], nombre=r[1], profesor_id=r[2], precio=r[3], max_alumnos=r[4])
            return None

def insert_asignatura(nombre: dict[str, str], profesor_id: int | None, precio: float = 0.0, max_alumnos: int = 30) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO asignaturas (nombre, profesor_id, precio, max_alumnos) VALUES (%s, %s, %s, %s)", (json.dumps(nombre), profesor_id, precio, max_alumnos))
        conn.commit()

def update_asignatura(asignatura_id: int, nombre: dict[str, str], profesor_id: int | None, precio: float, max_alumnos: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE asignaturas SET nombre = %s, profesor_id = %s, precio = %s, max_alumnos = %s WHERE asignatura_id = %s", (json.dumps(nombre), profesor_id, precio, max_alumnos, asignatura_id))
        conn.commit()

def delete_asignatura(asignatura_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM asignaturas WHERE asignatura_id = %s", (asignatura_id,))
        conn.commit()

def matricular_alumno_transaccional(alumno_id: int, asignatura_id: int) -> dict:
    with get_connection() as conn:
        conn.autocommit = False
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT alumno_id, nombre, saldo FROM alumnos WHERE alumno_id = %s FOR UPDATE",
                    (alumno_id,)
                )
                fila_alumno = cur.fetchone()
                if fila_alumno is None:
                    conn.rollback()
                    return {"ok": False, "error": "Alumno no encontrado"}

                _, nombre_alumno, saldo_alumno = fila_alumno

                cur.execute(
                    "SELECT asignatura_id, nombre, precio, max_alumnos FROM asignaturas WHERE asignatura_id = %s FOR UPDATE",
                    (asignatura_id,)
                )
                fila_asig = cur.fetchone()
                if fila_asig is None:
                    conn.rollback()
                    return {"ok": False, "error": "Asignatura no encontrada"}

                _, nombre_asig, precio, max_alumnos = fila_asig

                cur.execute(
                    "SELECT 1 FROM matriculas WHERE alumno_id = %s AND asignatura_id = %s",
                    (alumno_id, asignatura_id)
                )
                if cur.fetchone() is not None:
                    conn.rollback()
                    return {"ok": False, "error": "El alumno ya está matriculado en esta asignatura"}

                cur.execute(
                    "SELECT COUNT(*) FROM matriculas WHERE asignatura_id = %s",
                    (asignatura_id,)
                )
                inscritos = cur.fetchone()[0]
                if inscritos >= max_alumnos:
                    conn.rollback()
                    return {"ok": False, "error": f"No quedan plazas disponibles (límite: {max_alumnos})"}

                if saldo_alumno < precio:
                    conn.rollback()
                    return {"ok": False, "error": f"Saldo insuficiente (tienes {saldo_alumno}€, necesitas {precio}€)"}

                cur.execute(
                    "UPDATE alumnos SET saldo = saldo - %s WHERE alumno_id = %s",
                    (precio, alumno_id)
                )
                cur.execute(
                    "INSERT INTO matriculas (alumno_id, asignatura_id) VALUES (%s, %s)",
                    (alumno_id, asignatura_id)
                )

            conn.commit()
            return {
                "ok": True,
                "mensaje": "Matrícula realizada con éxito",
                "alumno": nombre_alumno,
                "asignatura": nombre_asig,
                "precio": float(precio),
                "saldo_restante": float(saldo_alumno - precio),
                "plazas_restantes": max_alumnos - inscritos - 1,
            }

        except Exception as e:
            conn.rollback()
            return {"ok": False, "error": f"Error interno: {e}"}

def get_asignaturas_con_plazas() -> list[dict]:
    """
    Devuelve las asignaturas con el número de alumnos inscritos y plazas libres.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    a.asignatura_id,
                    a.nombre,
                    a.precio,
                    a.max_alumnos,
                    COUNT(m.matricula_id) AS inscritos,
                    a.max_alumnos - COUNT(m.matricula_id) AS plazas_libres
                FROM asignaturas a
                LEFT JOIN matriculas m ON a.asignatura_id = m.asignatura_id
                GROUP BY a.asignatura_id, a.nombre, a.precio, a.max_alumnos
                ORDER BY a.asignatura_id;
            """)
            return [
                {
                    "id": r[0],
                    "nombre": r[1],
                    "precio": r[2],
                    "max_alumnos": r[3],
                    "inscritos": r[4],
                    "plazas_libres": r[5],
                }
                for r in cur.fetchall()
            ]
def get_vista_matriculas() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT nombre_alumno, nombre_profesor, nombre_asignatura FROM vista_matriculas_detalle;"
            )
            return [
                {
                    "nombre_alumno": r[0],
                    "nombre_profesor": r[1],
                    "nombre_asignatura": r[2],
                }
                for r in cur.fetchall()
            ]

# Filtros de busqueda
def search_alumnos(
    nombre: str | None = None,
    email: str | None = None,
    saldo_min: Decimal | None = None,
    saldo_max: Decimal | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Alumnos]:
    conditions: list[sql.Composable] = []
    params: list[Any] = []

    if nombre:
        conditions.append(sql.SQL("unaccent(nombre) ILIKE unaccent(%s)"))
        params.append(f"%{nombre}%")
    if email:
        conditions.append(sql.SQL("email_alumno ILIKE %s"))
        params.append(f"%{email}%")
    if saldo_min is not None:
        conditions.append(sql.SQL("saldo >= %s"))
        params.append(saldo_min)
    if saldo_max is not None:
        conditions.append(sql.SQL("saldo <= %s"))
        params.append(saldo_max)

    base = sql.SQL("SELECT alumno_id, nombre, email_alumno, saldo FROM alumnos")
    where = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions) if conditions else sql.SQL("")
    query = base + where + sql.SQL(" ORDER BY alumno_id LIMIT %s OFFSET %s")
    params += [limit, offset]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return [Alumnos(alumno_id=r[0], nombre=r[1], email_alumno=r[2], saldo=r[3]) for r in cur.fetchall()]


def search_profesores(
    nombre: str | None = None,
    email: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Profesores]:
    conditions: list[sql.Composable] = []
    params: list[Any] = []

    if nombre:
        conditions.append(sql.SQL("unaccent(nombre) ILIKE unaccent(%s)"))
        params.append(f"%{nombre}%")
    if email:
        conditions.append(sql.SQL("email_profesor ILIKE %s"))
        params.append(f"%{email}%")

    base = sql.SQL("SELECT profesor_id, nombre, email_profesor FROM profesores")
    where = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions) if conditions else sql.SQL("")
    query = base + where + sql.SQL(" ORDER BY profesor_id LIMIT %s OFFSET %s")
    params += [limit, offset]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return [Profesores(profesor_id=r[0], nombre=r[1], email_profesor=r[2]) for r in cur.fetchall()]


def search_asignaturas(
    nombre: str | None = None,
    idioma: str | None = None,
    modo_busqueda: str | None = None,
    precio_min: Decimal | None = None,
    precio_max: Decimal | None = None,
    max_alumnos_min: int | None = None,
    max_alumnos_max: int | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Asignaturas]:
    """Busca asignaturas con filtros dinámicos y paginación."""
    conditions: list[sql.Composable] = []
    params: list[Any] = []

    if nombre:
        lang_key = idioma if idioma in ('es', 'en') else 'es'
        if modo_busqueda == 'fts':
            pg_lang = 'spanish' if lang_key == 'es' else 'english'
            conditions.append(sql.SQL("to_tsvector(%s, nombre->>%s) @@ plainto_tsquery(%s, %s)"))
            params.extend([pg_lang, lang_key, pg_lang, nombre])
        else:
            conditions.append(sql.SQL("(nombre->>%s) %% %s"))
            params.extend([lang_key, nombre])
    if precio_min is not None:
        conditions.append(sql.SQL("precio >= %s"))
        params.append(precio_min)
    if precio_max is not None:
        conditions.append(sql.SQL("precio <= %s"))
        params.append(precio_max)
    if max_alumnos_min is not None:
        conditions.append(sql.SQL("max_alumnos >= %s"))
        params.append(max_alumnos_min)
    if max_alumnos_max is not None:
        conditions.append(sql.SQL("max_alumnos <= %s"))
        params.append(max_alumnos_max)

    base = sql.SQL("SELECT asignatura_id, nombre, profesor_id, precio, max_alumnos FROM asignaturas")
    where = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions) if conditions else sql.SQL("")
    query = base + where + sql.SQL(" ORDER BY asignatura_id LIMIT %s OFFSET %s")
    params += [limit, offset]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return [Asignaturas(asignatura_id=r[0], nombre=r[1], profesor_id=r[2], precio=r[3], max_alumnos=r[4]) for r in cur.fetchall()]


def search_matriculas(
    alumno_id: int | None = None,
    asignatura_id: int | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Matriculas]:
    """Busca matrículas por alumno, asignatura o rango de fechas, con paginación."""
    conditions: list[sql.Composable] = []
    params: list[Any] = []

    if alumno_id is not None:
        conditions.append(sql.SQL("alumno_id = %s"))
        params.append(alumno_id)
    if asignatura_id is not None:
        conditions.append(sql.SQL("asignatura_id = %s"))
        params.append(asignatura_id)
    if fecha_inicio is not None:
        conditions.append(sql.SQL("fecha_matricula >= %s"))
        params.append(fecha_inicio)
    if fecha_fin is not None:
        conditions.append(sql.SQL("fecha_matricula < %s::date + INTERVAL '1 day'"))
        params.append(fecha_fin)

    base = sql.SQL("SELECT matricula_id, alumno_id, asignatura_id, fecha_matricula FROM matriculas")
    where = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions) if conditions else sql.SQL("")
    query = base + where + sql.SQL(" ORDER BY matricula_id LIMIT %s OFFSET %s")
    params += [limit, offset]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return [Matriculas(matricula_id=r[0], alumno_id=r[1], asignatura_id=r[2], fecha_matricula=r[3]) for r in cur.fetchall()]


def search_alumnos_audit(
    nombre: str | None = None,
    email: str | None = None,
    operation: str | None = None,
    saldo_min: Decimal | None = None,
    saldo_max: Decimal | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[AlumnosAudit]:
    conditions: list[sql.Composable] = []
    params: list[Any] = []

    if nombre:
        conditions.append(sql.SQL("unaccent(nombre) ILIKE unaccent(%s)"))
        params.append(f"%{nombre}%")
    if email:
        conditions.append(sql.SQL("email_alumno ILIKE %s"))
        params.append(f"%{email}%")
    if operation:
        conditions.append(sql.SQL("operation = %s"))
        params.append(operation)
    if saldo_min is not None:
        conditions.append(sql.SQL("saldo >= %s"))
        params.append(saldo_min)
    if saldo_max is not None:
        conditions.append(sql.SQL("saldo <= %s"))
        params.append(saldo_max)
    if fecha_inicio is not None:
        conditions.append(sql.SQL("stamp >= %s"))
        params.append(fecha_inicio)
    if fecha_fin is not None:
        conditions.append(sql.SQL("stamp < %s::date + INTERVAL '1 day'"))
        params.append(fecha_fin)

    base = sql.SQL("SELECT audit_id, operation, stamp, userid, alumno_id, nombre, email_alumno, saldo, ST_AsText(ubicacion) FROM alumnos_audit")
    where = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions) if conditions else sql.SQL("")
    query = base + where + sql.SQL(" ORDER BY stamp DESC LIMIT %s OFFSET %s")
    params += [limit, offset]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return [AlumnosAudit(audit_id=r[0], operation=r[1], stamp=r[2], userid=r[3], alumno_id=r[4], nombre=r[5], email_alumno=r[6], saldo=r[7], ubicacion=r[8]) for r in cur.fetchall()]


def search_profesores_audit(
    nombre: str | None = None,
    email: str | None = None,
    operation: str | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[ProfesoresAudit]:
    conditions: list[sql.Composable] = []
    params: list[Any] = []

    if nombre:
        conditions.append(sql.SQL("unaccent(nombre) ILIKE unaccent(%s)"))
        params.append(f"%{nombre}%")
    if email:
        conditions.append(sql.SQL("email_profesor ILIKE %s"))
        params.append(f"%{email}%")
    if operation:
        conditions.append(sql.SQL("operation = %s"))
        params.append(operation)
    if fecha_inicio is not None:
        conditions.append(sql.SQL("stamp >= %s"))
        params.append(fecha_inicio)
    if fecha_fin is not None:
        conditions.append(sql.SQL("stamp < %s::date + INTERVAL '1 day'"))
        params.append(fecha_fin)

    base = sql.SQL("SELECT audit_id, operation, stamp, userid, profesor_id, nombre, email_profesor FROM profesores_audit")
    where = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions) if conditions else sql.SQL("")
    query = base + where + sql.SQL(" ORDER BY stamp DESC LIMIT %s OFFSET %s")
    params += [limit, offset]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return [ProfesoresAudit(audit_id=r[0], operation=r[1], stamp=r[2], userid=r[3], profesor_id=r[4], nombre=r[5], email_profesor=r[6]) for r in cur.fetchall()]


def search_asignaturas_audit(
    nombre: str | None = None,
    idioma: str | None = None,
    modo_busqueda: str | None = None,
    operation: str | None = None,
    precio_min: Decimal | None = None,
    precio_max: Decimal | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[AsignaturasAudit]:
    conditions: list[sql.Composable] = []
    params: list[Any] = []

    if nombre:
        lang_key = idioma if idioma in ('es', 'en') else 'es'
        if modo_busqueda == 'fts':
            pg_lang = 'spanish' if lang_key == 'es' else 'english'
            conditions.append(sql.SQL("to_tsvector(%s, nombre->>%s) @@ plainto_tsquery(%s, %s)"))
            params.extend([pg_lang, lang_key, pg_lang, nombre])
        else:
            conditions.append(sql.SQL("(nombre->>%s) %% %s"))
            params.extend([lang_key, nombre])
    if operation:
        conditions.append(sql.SQL("operation = %s"))
        params.append(operation)
    if precio_min is not None:
        conditions.append(sql.SQL("precio >= %s"))
        params.append(precio_min)
    if precio_max is not None:
        conditions.append(sql.SQL("precio <= %s"))
        params.append(precio_max)
    if fecha_inicio is not None:
        conditions.append(sql.SQL("stamp >= %s"))
        params.append(fecha_inicio)
    if fecha_fin is not None:
        conditions.append(sql.SQL("stamp < %s::date + INTERVAL '1 day'"))
        params.append(fecha_fin)

    base = sql.SQL("SELECT audit_id, operation, stamp, userid, asignatura_id, profesor_id, nombre, precio, max_alumnos FROM asignaturas_audit")
    where = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions) if conditions else sql.SQL("")
    query = base + where + sql.SQL(" ORDER BY stamp DESC LIMIT %s OFFSET %s")
    params += [limit, offset]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return [AsignaturasAudit(audit_id=r[0], operation=r[1], stamp=r[2], userid=r[3], asignatura_id=r[4], profesor_id=r[5], nombre=r[6], precio=r[7], max_alumnos=r[8]) for r in cur.fetchall()]


# Consultas OLAP
def get_olap_row_number() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                WITH gastos_por_mes AS (
                    -- Paso 1: Calculamos lo que gasta cada alumno en cada mes
                    SELECT 
                        TO_CHAR(m.fecha_matricula, 'YYYY-MM') as mes,
                        a.nombre as alumno_nombre,
                        SUM(asig.precio) as total_gastado
                    FROM alumnos a
                    JOIN matriculas m ON a.alumno_id = m.alumno_id
                    JOIN asignaturas asig ON m.asignatura_id = asig.asignatura_id
                    GROUP BY TO_CHAR(m.fecha_matricula, 'YYYY-MM'), a.alumno_id, a.nombre
                ),
                ranking_mes AS (
                    -- Paso 2: Asignamos el número de fila (ranking) DENTRO de cada mes
                    SELECT 
                        mes,
                        alumno_nombre,
                        total_gastado,
                        ROW_NUMBER() OVER (PARTITION BY mes ORDER BY total_gastado DESC) as ranking
                    FROM gastos_por_mes
                )
                -- Paso 3: Filtramos solo el Top 3 de cada mes
                SELECT 
                    mes,
                    alumno_nombre,
                    total_gastado,
                    ranking
                FROM ranking_mes
                WHERE ranking <= 3
                ORDER BY mes DESC, ranking ASC;
            """)
            return [
                {
                    "mes": r[0],
                    "alumno_nombre": r[1],
                    "total_gastado": float(r[2]) if r[2] is not None else 0.0,
                    "ranking": r[3]
                }
                for r in cur.fetchall()
            ]


def get_olap_grouping_sets() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    p.nombre as profesor,
                    asig.nombre->>'es' as asignatura,
                    COUNT(m.matricula_id) as total_matriculas,
                    SUM(asig.precio) as ingresos_totales,
                    GROUPING(p.nombre) as g_profesor,
                    GROUPING(asig.nombre->>'es') as g_asignatura
                FROM matriculas m
                JOIN asignaturas asig ON m.asignatura_id = asig.asignatura_id
                LEFT JOIN profesores p ON asig.profesor_id = p.profesor_id
                GROUP BY GROUPING SETS (
                    (p.nombre, asig.nombre->>'es'),
                    (p.nombre),
                    ()
                )
                ORDER BY p.nombre NULLS LAST, asig.nombre->>'es' NULLS LAST;
            """)
            
            resultados = []
            for r in cur.fetchall():
                prof_val = r[0]
                asig_val = r[1]
                total_matriculas = r[2]
                ingresos = r[3]
                g_prof = r[4]
                g_asig = r[5]
                
                resultados.append({
                    "profesor": "Todos los profesores" if g_prof == 1 else prof_val,
                    "asignatura": "Todas las asignaturas" if g_asig == 1 else asig_val,
                    "total_matriculas": total_matriculas,
                    "ingresos_totales": float(ingresos) if ingresos is not None else 0.0,
                    "es_total_profesor": bool(g_prof),
                    "es_total_asignatura": bool(g_asig)
                })
                
            return resultados


def get_olap_rollup() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    TO_CHAR(m.fecha_matricula, 'YYYY') as anio,
                    TO_CHAR(m.fecha_matricula, 'MM') as mes,
                    COUNT(*) as total_matriculas,
                    SUM(asig.precio) as ingresos,
                    GROUPING(TO_CHAR(m.fecha_matricula, 'YYYY')) as g_anio,
                    GROUPING(TO_CHAR(m.fecha_matricula, 'MM')) as g_mes
                FROM matriculas m
                JOIN asignaturas asig ON m.asignatura_id = asig.asignatura_id
                GROUP BY ROLLUP (
                    TO_CHAR(m.fecha_matricula, 'YYYY'),
                    TO_CHAR(m.fecha_matricula, 'MM')
                )
                ORDER BY 
                    TO_CHAR(m.fecha_matricula, 'YYYY') NULLS LAST, 
                    TO_CHAR(m.fecha_matricula, 'MM') NULLS LAST;
            """)
            
            resultados = []
            for r in cur.fetchall():
                anio_val = r[0]
                mes_val = r[1]
                total_matriculas = r[2]
                ingresos = r[3]
                g_anio = r[4]
                g_mes = r[5]
                
                resultados.append({
                    "anio": "Todos los años" if g_anio == 1 else anio_val,
                    "mes": "Todos los meses" if g_mes == 1 else mes_val,
                    "total_matriculas": total_matriculas,
                    "ingresos": float(ingresos) if ingresos is not None else 0.0,
                    "es_total_anio": bool(g_anio),
                    "es_total_mes": bool(g_mes)
                })
                
            return resultados


def get_olap_filter() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    p.nombre as profesor,
                    COUNT(m.matricula_id) FILTER (WHERE asig.precio > 50) as matriculas_caras,
                    COUNT(m.matricula_id) FILTER (WHERE asig.precio <= 50) as matriculas_baratas,
                    COUNT(m.matricula_id) as total_matriculas
                FROM profesores p
                JOIN asignaturas asig ON p.profesor_id = asig.profesor_id
                LEFT JOIN matriculas m ON asig.asignatura_id = m.asignatura_id
                GROUP BY p.profesor_id, p.nombre
                ORDER BY total_matriculas DESC;
            """)
            return [
                {
                    "profesor": r[0],
                    "matriculas_caras": r[1],
                    "matriculas_baratas": r[2],
                    "total_matriculas": r[3]
                }
                for r in cur.fetchall()
            ]

def viajar_alumno_aula(alumno_id: int, asignatura_id: int) -> dict:
    """
    Calcula la distancia entre un alumno y el aula (área) de una asignatura,
    y actualiza la ubicación del alumno al centro de dicha aula.
    """
    with get_connection() as conn:
        conn.autocommit = False
        try:
            with conn.cursor() as cur:
                # Obtenemos la distancia y el nuevo punto (centro del aula)
                cur.execute("""
                    SELECT 
                        ST_Distance(al.ubicacion::geography, asig.area::geography) as distancia_metros,
                        ST_Centroid(asig.area) as nuevo_punto
                    FROM alumnos al
                    CROSS JOIN asignaturas asig
                    WHERE al.alumno_id = %s AND asig.asignatura_id = %s
                """, (alumno_id, asignatura_id))
                
                row = cur.fetchone()
                if not row:
                    conn.rollback()
                    return {"ok": False, "error": "Alumno o asignatura no encontrados."}
                
                distancia, nuevo_punto = row
                
                if distancia is None or nuevo_punto is None:
                    conn.rollback()
                    return {"ok": False, "error": "El alumno o la asignatura no tienen ubicación GIS definida."}
                
                # Actualizamos la ubicación del alumno
                cur.execute("""
                    UPDATE alumnos 
                    SET ubicacion = %s 
                    WHERE alumno_id = %s
                """, (nuevo_punto, alumno_id))
                
                conn.commit()
                return {
                    "ok": True,
                    "mensaje": "Viaje completado exitosamente.",
                    "distancia_metros": round(distancia, 2)
                }
        except Exception as e:
            conn.rollback()
            return {"ok": False, "error": f"Error interno: {e}"}