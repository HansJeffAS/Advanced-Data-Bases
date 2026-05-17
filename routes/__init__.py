# Blueprints: rutas agrupadas por recurso.

from routes.main import main_bp
from routes.alumnos import alumnos_bp
from routes.profesores import profesores_bp
from routes.asignaturas import asignaturas_bp
from routes.matriculas import matriculas_bp

__all__ = ["main_bp", "alumnos_bp", "profesores_bp", "asignaturas_bp", "matriculas_bp"]
