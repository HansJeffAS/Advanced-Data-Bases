"""Rutas del recurso asignaturas."""
from __future__ import annotations

from flask import Blueprint, render_template

from flask import request

from models.entities import AsignaturasAudit

from models.db import get_asignaturas

from models.db import get_asignaturas, get_auditoria_general, get_auditoria_asignatura

asignaturas_bp = Blueprint("asignaturas", __name__, url_prefix="/asignaturas")


@asignaturas_bp.route("")
def list_():
    asignaturas = get_asignaturas()
    return render_template("asignaturas.html", asignaturas=asignaturas)

@asignaturas_bp.route("/auditoria/general")
def auditoria_general():
    search_query = request.args.get('search')
    
    # Caso A: El usuario no ha escrito nada todavía (Carga inicial)
    if search_query is None:
        historial = get_auditoria_general("asignaturas_audit", AsignaturasAudit)
        titulo = "General"

    # Caso B: El usuario escribió un número (Búsqueda válida)
    elif search_query.isdigit():
        historial = get_auditoria_asignatura(search_query)
        titulo = f"Filtrado por ID: {search_query}"

    # Caso C: El usuario escribió letras o símbolos (Búsqueda inválida)
    else:
        historial = [] # Enviamos una lista vacía
        titulo = f"Sin resultados para: '{search_query}' (Solo se permiten IDs numéricos)"
        
    return render_template(
        "auditoria_asignaturas.html", 
        auditoria=historial, 
        id_asignatura=titulo
    )