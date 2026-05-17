from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Alumnos:
    """Alumno matriculado"""
    id: int
    name: str
    email: str


@dataclass(frozen=True)
class Profesores:
    """Profesores"""
    id: int
    name: str
    email: str
   
@dataclass(frozen=True)
class Asignaturas:
    id: int
    name: str
    id_profesor: int

@dataclass(frozen=True)
class Matriculas:
    id: int
    alumno_id: int
    asignatura_id: int
    fecha: str

# Estructuras para los históricos de auditorías
@dataclass(frozen=True)
class AlumnosAudit:
    audit_id: int
    operation: str
    stamp: str  # Tambien podemos usar datedatetime
    userid: str
    alumno_id: int
    nombre: str
    email_alumno: str

@dataclass(frozen=True)
class ProfesoresAudit:
    audit_id: int
    operation: str
    stamp: str  # Tambien podemos usar datedatetime
    userid: str
    profesor_id: int
    nombre: str
    email_profesor: str

@dataclass(frozen=True)
class AsignaturasAudit:
    audit_id: int
    operation: str
    stamp: str  # Tambien podemos usar datedatetime
    userid: str
    asignatura_id: int
    profesor_id: int
    nombre: str