from __future__ import annotations

import psycopg

from config import load_config

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
                "SELECT alumno_id, nombre, email_alumno FROM alumnos ORDER BY alumno_id;"
            )
            return [Alumnos(id=r[0], name=r[1], email=r[2]) for r in cur.fetchall()]

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
                "SELECT asignatura_id, nombre, profesor_id FROM asignaturas ORDER BY asignatura_id;"
            )
            return [Asignaturas(id=r[0], name=r[1], id_profesor=r[2]) for r in cur.fetchall()]
        
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
        
def get_auditoria_alumno(alumno: str) -> list[AlumnosAudit]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Solo filtramos por profesor_id usando el comparador de igualdad (=)
            query = """
                SELECT audit_id, operation, stamp, userid, alumno_id, nombre, email_alumno 
                FROM alumnos_audit 
                WHERE alumno_id = %s
                ORDER BY stamp DESC;
            """
            try:
                # Convertimos a int para asegurar que sea una búsqueda numérica
                cur.execute(query, (int(alumno),))
            except ValueError:
                # Si el usuario escribe letras en lugar de números, retornamos lista vacía
                return []
            
            return [
                AlumnosAudit(
                    audit_id=r[0], operation=r[1], stamp=r[2], 
                    userid=r[3], alumno_id=r[4], nombre=r[5], email_alumno=r[6]
                ) for r in cur.fetchall()
            ]

def get_auditoria_profesor(profesor: str) -> list[ProfesoresAudit]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Solo filtramos por profesor_id usando el comparador de igualdad (=)
            query = """
                SELECT audit_id, operation, stamp, userid, profesor_id, nombre, email_profesor 
                FROM profesores_audit 
                WHERE profesor_id = %s
                ORDER BY stamp DESC;
            """
            try:
                # Convertimos a int para asegurar que sea una búsqueda numérica
                cur.execute(query, (int(profesor),))
            except ValueError:
                # Si el usuario escribe letras en lugar de números, retornamos lista vacía
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
            # Solo filtramos por profesor_id usando el comparador de igualdad (=)
            query = """
                SELECT audit_id, operation, stamp, userid, asignatura_id, profesor_id, nombre 
                FROM asignaturas_audit 
                WHERE asignatura_id = %s
                ORDER BY stamp DESC;
            """
            try:
                # Convertimos a int para asegurar que sea una búsqueda numérica
                cur.execute(query, (int(asignatura),))
            except ValueError:
                # Si el usuario escribe letras en lugar de números, retornamos lista vacía
                return []
            
            return [
                AsignaturasAudit(
                    audit_id=r[0], operation=r[1], stamp=r[2], 
                    userid=r[3], asignatura_id=r[4], profesor_id=r[5], nombre=r[6]
                ) for r in cur.fetchall()
            ]