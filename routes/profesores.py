"""Rutas del recurso profesor."""
from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for

from models.entities import ProfesoresAudit

from models.db import get_profesores, get_auditoria_general, get_auditoria_por_id, insert_profesor, update_profesor, delete_profesor, get_profesor

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
        # Llamamos a la función genérica pasándole los datos de Alumnos
        historial = get_auditoria_por_id(
            tabla="profesores_audit", 
            columna_id="profesor_id", 
            valor_id=search_query, 
            modelo=ProfesoresAudit
        )
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

@profesores_bp.route("/add", methods=["POST"])
def add():
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    if nombre and email:
        insert_profesor(nombre, email)
    return redirect(url_for("profesores.list_"))

@profesores_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        if nombre and email:
            update_profesor(id, nombre, email)
        return redirect(url_for("profesores.list_"))
    
    profesor = get_profesor(id)
    if not profesor:
        return redirect(url_for("profesores.list_"))
    return render_template("profesores_edit.html", profesor=profesor)

@profesores_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    delete_profesor(id)
    return redirect(url_for("profesores.list_"))