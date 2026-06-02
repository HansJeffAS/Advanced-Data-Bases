from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Alumnos:
    alumno_id: int
    nombre: str
    email_alumno: str
    saldo: Decimal


@dataclass(frozen=True)
class Profesores:
    profesor_id: int
    nombre: str
    email_profesor: str
   
@dataclass(frozen=True)
class Asignaturas:
    asignatura_id: int
    profesor_id: int
    nombre: dict[str, str]
    precio: Decimal
    max_alumnos: int

@dataclass(frozen=True)
class Matriculas:
    matricula_id: int
    asignatura_id: int
    alumno_id: int
    fecha_matricula: str

@dataclass(frozen=True)
class AlumnosAudit:
    audit_id: int
    operation: str
    stamp: str
    userid: str
    alumno_id: int
    nombre: str
    email_alumno: str
    saldo: Decimal

@dataclass(frozen=True)
class ProfesoresAudit:
    audit_id: int
    operation: str
    stamp: str
    userid: str
    profesor_id: int
    nombre: str
    email_profesor: str

@dataclass(frozen=True)
class AsignaturasAudit:
    audit_id: int
    operation: str
    stamp: str
    userid: str
    asignatura_id: int
    profesor_id: int
    nombre: dict[str, str]
    precio: Decimal
    max_alumnos: int