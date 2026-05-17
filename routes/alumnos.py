"""Rutas del recurso alumnos."""
from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for

from models.entities import AlumnosAudit

from models.db import get_alumnos, get_auditoria_general, get_auditoria_alumno, insert_alumno, update_alumno, delete_alumno, get_alumno

alumnos_bp = Blueprint("alumnos", __name__, url_prefix="/alumnos")

@alumnos_bp.route("")
def list_():
    alumnos = get_alumnos()
    return render_template("alumnos.html", alumnos=alumnos)

@alumnos_bp.route("/auditoria/general")
def auditoria_general():
    search_query = request.args.get('search')
    
    # Caso A: El usuario no ha escrito nada todavía (Carga inicial)
    if search_query is None:
        historial = get_auditoria_general(tabla="alumnos_audit", modelo=AlumnosAudit)
        titulo = "General"

    # Caso B: El usuario escribió un número (Búsqueda válida)
    elif search_query.isdigit():
        historial = get_auditoria_alumno(search_query)
        titulo = f"Filtrado por ID: {search_query}"

    # Caso C: El usuario escribió letras o símbolos (Búsqueda inválida)
    else:
        historial = [] # Enviamos una lista vacía
        titulo = f"Sin resultados para: '{search_query}' (Solo se permiten IDs numéricos)"
        
    return render_template(
        "auditoria_alumnos.html",
        auditoria=historial, 
        id_profe=titulo
    )

@alumnos_bp.route("/add", methods=["POST"])
def add():
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    if nombre and email:
        insert_alumno(nombre, email)
    return redirect(url_for("alumnos.list_"))

@alumnos_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        if nombre and email:
            update_alumno(id, nombre, email)
        return redirect(url_for("alumnos.list_"))
    
    alumno = get_alumno(id)
    if not alumno:
        return redirect(url_for("alumnos.list_"))
    return render_template("alumnos_edit.html", alumno=alumno)

@alumnos_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    delete_alumno(id)
    return redirect(url_for("alumnos.list_"))