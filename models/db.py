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
                "SELECT alumno_id, nombre, email_alumno, saldo FROM alumnos ORDER BY alumno_id;"
            )
            return [Alumnos(id=r[0], name=r[1], email=r[2], saldo=r[3]) for r in cur.fetchall()]

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
                "SELECT asignatura_id, nombre, profesor_id, precio, max_alumnos FROM asignaturas ORDER BY asignatura_id;"
            )
            return [Asignaturas(id=r[0], name=r[1], id_profesor=r[2], precio=r[3], max_alumnos=r[4]) for r in cur.fetchall()]
        
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
                SELECT audit_id, operation, stamp, userid, alumno_id, nombre, email_alumno, saldo
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
                    userid=r[3], alumno_id=r[4], nombre=r[5], email_alumno=r[6], saldo=r[7]
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
                SELECT audit_id, operation, stamp, userid, asignatura_id, profesor_id, nombre, precio, max_alumnos
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
                    userid=r[3], asignatura_id=r[4], profesor_id=r[5], nombre=r[6],
                    precio=r[7], max_alumnos=r[8]
                ) for r in cur.fetchall()
            ]

# --- CRUD Alumnos ---
def get_alumno(alumno_id: int) -> Alumnos | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT alumno_id, nombre, email_alumno, saldo FROM alumnos WHERE alumno_id = %s", (alumno_id,))
            r = cur.fetchone()
            if r:
                return Alumnos(id=r[0], name=r[1], email=r[2], saldo=r[3])
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
            cur.execute("SELECT asignatura_id, nombre, profesor_id, precio, max_alumnos FROM asignaturas WHERE asignatura_id = %s", (asignatura_id,))
            r = cur.fetchone()
            if r:
                return Asignaturas(id=r[0], name=r[1], id_profesor=r[2], precio=r[3], max_alumnos=r[4])
            return None

def insert_asignatura(nombre: str, profesor_id: int | None, precio: float = 0.0, max_alumnos: int = 30) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO asignaturas (nombre, profesor_id, precio, max_alumnos) VALUES (%s, %s, %s, %s)", (nombre, profesor_id, precio, max_alumnos))
        conn.commit()

def update_asignatura(asignatura_id: int, nombre: str, profesor_id: int | None, precio: float, max_alumnos: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE asignaturas SET nombre = %s, profesor_id = %s, precio = %s, max_alumnos = %s WHERE asignatura_id = %s", (nombre, profesor_id, precio, max_alumnos, asignatura_id))
        conn.commit()

def delete_asignatura(asignatura_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM asignaturas WHERE asignatura_id = %s", (asignatura_id,))
        conn.commit()

# --- Matriculación transaccional ---
def matricular_alumno_transaccional(alumno_id: int, asignatura_id: int) -> dict:
    """
    Llama a la función PL/pgSQL matricular_alumno que gestiona toda la lógica
    transaccional: verificación de plazas, saldo y descuento dentro de una
    única transacción atómica en el servidor.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT matricular_alumno(%s, %s);",
                (alumno_id, asignatura_id)
            )
            resultado = cur.fetchone()[0]
        conn.commit()
    return resultado

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