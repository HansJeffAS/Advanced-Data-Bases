from __future__ import annotations

import psycopg

from config import load_config

from typing import TypeVar, Type, Any

from decimal import Decimal

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
                "SELECT alumno_id, nombre, email_alumno, dinero FROM alumnos ORDER BY alumno_id;"
            )
            return [Alumnos(id=r[0], name=r[1], email=r[2], money=r[3]) for r in cur.fetchall()]

def get_profesores() -> list[Profesores]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT profesor_id, nombre, email_profesor FROM profesores ORDER BY profesor_id;"
            )
            return [Profesores(id=r[0], name=r[1], email=r[2]) for r in cur.fetchall()]
        
def get_asignaturas() -> list[Asignaturas]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT asignatura_id, nombre, profesor_id, costo, cupo_maximo FROM asignaturas ORDER BY asignatura_id;"
            )
            return [Asignaturas(id=r[0], name=r[1], id_profesor=r[2], cost=r[3], max_capacity=r[4]) for r in cur.fetchall()]
        
def get_matriculas() -> list[Matriculas]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT matricula_id, alumno_id, asignatura_id, fecha_matricula FROM matriculas ORDER BY matricula_id;"
            )
            return [Matriculas(id=r[0], alumno_id=r[1], asignatura_id=r[2], fecha=r[3]) for r in cur.fetchall()]

# Definimos un tipo genérico T
T = TypeVar("T")

def get_auditoria_general(tabla: str, modelo: Type[T]) -> list[T]:
    """
    Obtiene registros de auditoría de cualquier tabla.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = f"SELECT * FROM {tabla} ORDER BY stamp DESC;"
            cur.execute(query)
            # Usamos el desempaquetado de argumentos (*r) para que la clase 
            # se encargue de asignar los valores a sus atributos.
            return [modelo(*r) for r in cur.fetchall()]
        
def get_auditoria_por_id(tabla: str, columna_id: str, valor_id: str, modelo: Type[T]) -> list[T]:
    """
    Busca el historial de auditoría en cualquier tabla filtrando por un ID específico.
    Sirve para Alumnos, Profesores y Asignaturas.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Construimos la query dinámicamente con la tabla y columna correspondientes
            query = f"""
                SELECT * FROM {tabla} 
                WHERE {columna_id} = %s
                ORDER BY stamp DESC;
            """
            try:
                # Intentamos convertir el ID a entero por seguridad
                cur.execute(query, (int(valor_id),))
            except ValueError:
                # Si el usuario escribió letras, devolvemos lista vacía sin romper la BD
                return []
            
            # Usamos (*r) para que Python asigne automáticamente cada columna 
            # de la fila a los atributos de la dataclass (modelo)
            return [modelo(*r) for r in cur.fetchall()]

# --- CRUD Alumnos ---
def get_alumno(alumno_id: int) -> Alumnos | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT alumno_id, nombre, email_alumno, dinero FROM alumnos WHERE alumno_id = %s", (alumno_id,))
            r = cur.fetchone()
            if r:
                return Alumnos(id=r[0], name=r[1], email=r[2], money=r[3])
            return None

def insert_alumno(nombre: str, email_alumno: str, dinero: Decimal) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO alumnos (nombre, email_alumno, dinero) VALUES (%s, %s, %s)", (nombre, email_alumno, dinero))
        conn.commit()

def update_alumno(alumno_id: int, nombre: str, email_alumno: str, dinero: Decimal) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE alumnos SET nombre = %s, email_alumno = %s, dinero = %s WHERE alumno_id = %s", (nombre, email_alumno, dinero, alumno_id))
        conn.commit()

def delete_alumno(alumno_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM alumnos WHERE alumno_id = %s", (alumno_id,))
        conn.commit()

# --- CRUD Profesores ---
def get_profesor(profesor_id: int) -> Profesores | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT profesor_id, nombre, email_profesor FROM profesores WHERE profesor_id = %s", (profesor_id,))
            r = cur.fetchone()
            if r:
                return Profesores(id=r[0], name=r[1], email=r[2])
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

# --- CRUD Asignaturas ---
def get_asignatura(asignatura_id: int) -> Asignaturas | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT asignatura_id, nombre, profesor_id, costo, cupo_maximo FROM asignaturas WHERE asignatura_id = %s", (asignatura_id,))
            r = cur.fetchone()
            if r:
                return Asignaturas(id=r[0], name=r[1], id_profesor=r[2], cost=r[3], max_capacity=[4])
            return None

def insert_asignatura(nombre: str, profesor_id: int, dinero: Decimal| None) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO asignaturas (nombre, profesor_id, costo) VALUES (%s, %s, %s)", (nombre, profesor_id, dinero))
        conn.commit()

def update_asignatura(asignatura_id: int, nombre: str, profesor_id: int | None) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE asignaturas SET nombre = %s, profesor_id = %s WHERE asignatura_id = %s", (nombre, profesor_id, asignatura_id))
        conn.commit()

def delete_asignatura(asignatura_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM asignaturas WHERE asignatura_id = %s", (asignatura_id,))
        conn.commit()