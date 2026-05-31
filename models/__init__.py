# Capa Model del MVC: acceso a datos (PostgreSQL) y entidades de dominio.

from models.db import (
    get_connection,
    get_alumnos,
    get_profesores,
    get_asignaturas,
    get_matriculas,
    get_auditoria_general,
    get_auditoria_por_id
)
from models.entities import Alumnos, Profesores, Asignaturas, Matriculas, AlumnosAudit, ProfesoresAudit, AsignaturasAudit

__all__ = [
    "Alumnos",
    "Profesores",
    "Asignaturas",
    "Matriculas", 
    "AlumnosAudit",
    "ProfesoresAudit",
    "AsignaturasAudit",
    "get_connection",
    "get_alumnos",
    "get_profesores",
    "get_asignaturas",
    "get_matriculas",
    "get_auditoria_general",
    "get_auditoria_por_id"
]