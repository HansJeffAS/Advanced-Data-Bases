"""Rutas del recurso asignaturas."""
from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for

from models.entities import AsignaturasAudit

from models.db import (
    get_asignaturas, get_auditoria_general, get_auditoria_asignatura,
    get_profesores, insert_asignatura, update_asignatura, delete_asignatura,
    get_asignatura, get_asignaturas_con_plazas
)

asignaturas_bp = Blueprint("asignaturas", __name__, url_prefix="/asignaturas")


@asignaturas_bp.route("")
def list_():
    asignaturas = get_asignaturas()
    profesores = get_profesores()
    return render_template("asignaturas.html", asignaturas=asignaturas, profesores=profesores)

@asignaturas_bp.route("/catalogo")
def catalogo():
    asignaturas = get_asignaturas_con_plazas()
    return render_template("asignaturas_catalogo.html", asignaturas=asignaturas)

@asignaturas_bp.route("/auditoria/general")
def auditoria_general():
    historial = get_auditoria_general("asignaturas_audit", AsignaturasAudit)
    return render_template(
        "auditoria_asignaturas.html",
        auditoria=historial
    )

@asignaturas_bp.route("/add", methods=["POST"])
def add():
    nombre = request.form.get("nombre")
    profesor_id = request.form.get("profesor_id")
    precio_str = request.form.get("precio", "0")
    max_alumnos_str = request.form.get("max_alumnos", "30")

    if profesor_id:
        profesor_id = int(profesor_id)
    else:
        profesor_id = None

    try:
        precio = float(precio_str)
    except ValueError:
        precio = 0.0

    try:
        max_alumnos = int(max_alumnos_str)
    except ValueError:
        max_alumnos = 30
        
    if nombre:
        insert_asignatura(nombre, profesor_id, precio, max_alumnos)
    return redirect(url_for("asignaturas.list_"))

@asignaturas_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if request.method == "POST":
        nombre = request.form.get("nombre")
        profesor_id = request.form.get("profesor_id")
        precio_str = request.form.get("precio", "0")
        max_alumnos_str = request.form.get("max_alumnos", "30")

        if profesor_id:
            profesor_id = int(profesor_id)
        else:
            profesor_id = None
            
        try:
            precio = float(precio_str)
        except ValueError:
            precio = 0.0

        try:
            max_alumnos = int(max_alumnos_str)
        except ValueError:
            max_alumnos = 30

        if nombre:
            update_asignatura(id, nombre, profesor_id, precio, max_alumnos)
        return redirect(url_for("asignaturas.list_"))
    
    asignatura = get_asignatura(id)
    if not asignatura:
        return redirect(url_for("asignaturas.list_"))
    profesores = get_profesores()
    return render_template("asignaturas_edit.html", asignatura=asignatura, profesores=profesores)

@asignaturas_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    delete_asignatura(id)
    return redirect(url_for("asignaturas.list_"))