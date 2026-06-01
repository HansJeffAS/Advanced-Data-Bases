"""Rutas del recurso asignaturas."""
from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for

from models.db import (
    get_asignaturas, get_profesores, insert_asignatura, update_asignatura, delete_asignatura,
    get_asignatura, get_asignaturas_con_plazas,
    search_asignaturas, search_asignaturas_audit,
)
from tools.parse_params import parse_str, parse_decimal, parse_int, parse_date, parse_limit_offset

asignaturas_bp = Blueprint("asignaturas", __name__, url_prefix="/asignaturas")


@asignaturas_bp.route("")
def list_():
    asignaturas = get_asignaturas()
    profesores = get_profesores()
    return render_template("asignaturas.html", asignaturas=asignaturas, profesores=profesores)

@asignaturas_bp.route("/buscar")
def buscar():
    nombre = parse_str(request.args.get("nombre"))
    precio_min = parse_decimal(request.args.get("precio_min"))
    precio_max = parse_decimal(request.args.get("precio_max"))
    max_alumnos_min = parse_int(request.args.get("max_alumnos_min"))
    max_alumnos_max = parse_int(request.args.get("max_alumnos_max"))
    limit, offset = parse_limit_offset(request.args)

    asignaturas = search_asignaturas(
        nombre=nombre,
        precio_min=precio_min, precio_max=precio_max,
        max_alumnos_min=max_alumnos_min, max_alumnos_max=max_alumnos_max,
        limit=limit, offset=offset,
    )
    profesores = get_profesores()
    return render_template(
        "asignaturas.html",
        asignaturas=asignaturas,
        profesores=profesores,
        busqueda=True,
        params=request.args,
        limit=limit,
        offset=offset,
    )

@asignaturas_bp.route("/catalogo")
def catalogo():
    asignaturas = get_asignaturas_con_plazas()
    return render_template("asignaturas_catalogo.html", asignaturas=asignaturas)


@asignaturas_bp.route("/auditoria/buscar")
def auditoria_buscar():
    nombre = parse_str(request.args.get("nombre"))
    operation = parse_str(request.args.get("operation"))
    precio_min = parse_decimal(request.args.get("precio_min"))
    precio_max = parse_decimal(request.args.get("precio_max"))
    fecha_inicio = parse_date(request.args.get("fecha_inicio"))
    fecha_fin = parse_date(request.args.get("fecha_fin"))
    limit, offset = parse_limit_offset(request.args)

    historial = search_asignaturas_audit(
        nombre=nombre, operation=operation,
        precio_min=precio_min, precio_max=precio_max,
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
        limit=limit, offset=offset,
    )
    return render_template(
        "auditoria_asignaturas.html",
        auditoria=historial,
        busqueda=True,
        params=request.args,
        limit=limit,
        offset=offset,
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