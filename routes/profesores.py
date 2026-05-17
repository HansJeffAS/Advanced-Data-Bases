"""Rutas del recurso profesor."""
from __future__ import annotations

from flask import Blueprint, render_template

from flask import request

from models.entities import ProfesoresAudit

from models.db import get_profesores, get_auditoria_general, get_auditoria_profesor

profesores_bp = Blueprint("profesores", __name__, url_prefix="/profesores")

@profesores_bp.route("")
def list_():
    profesores = get_profesores()
    return render_template("profesores.html", profesores=profesores)

@profesores_bp.route("/auditoria/general")
def auditoria_general():
    search_query = request.args.get('search')
    
    # Caso A: El usuario no ha escrito nada todavía (Carga inicial)
    if search_query is None:
        historial = get_auditoria_general("profesores_audit", ProfesoresAudit)
        titulo = "General"

    # Caso B: El usuario escribió un número (Búsqueda válida)
    elif search_query.isdigit():
        historial = get_auditoria_profesor(search_query)
        titulo = f"Filtrado por ID: {search_query}"

    # Caso C: El usuario escribió letras o símbolos (Búsqueda inválida)
    else:
        historial = [] # Enviamos una lista vacía
        titulo = f"Sin resultados para: '{search_query}' (Solo se permiten IDs numéricos)"
        
    return render_template(
        "auditoria_profesores.html", 
        auditoria=historial, 
        id_profe=titulo
    )