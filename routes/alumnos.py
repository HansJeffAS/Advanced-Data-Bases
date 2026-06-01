"""Rutas del recurso alumnos."""
from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for

from models.db import (
    get_alumnos, insert_alumno, update_alumno, delete_alumno, get_alumno,
    search_alumnos, search_alumnos_audit,
)
from tools.parse_params import parse_str, parse_decimal, parse_date, parse_limit_offset

alumnos_bp = Blueprint("alumnos", __name__, url_prefix="/alumnos")

@alumnos_bp.route("")
def list_():
    alumnos = get_alumnos()
    return render_template("alumnos.html", alumnos=alumnos)

@alumnos_bp.route("/buscar")
def buscar():
    nombre = parse_str(request.args.get("nombre"))
    email = parse_str(request.args.get("email"))
    saldo_min = parse_decimal(request.args.get("saldo_min"))
    saldo_max = parse_decimal(request.args.get("saldo_max"))
    limit, offset = parse_limit_offset(request.args)

    alumnos = search_alumnos(
        nombre=nombre, email=email,
        saldo_min=saldo_min, saldo_max=saldo_max,
        limit=limit, offset=offset,
    )
    return render_template(
        "alumnos.html",
        alumnos=alumnos,
        busqueda=True,
        params=request.args,
        limit=limit,
        offset=offset,
    )


@alumnos_bp.route("/auditoria/buscar")
def auditoria_buscar():
    nombre = parse_str(request.args.get("nombre"))
    email = parse_str(request.args.get("email"))
    operation = parse_str(request.args.get("operation"))
    saldo_min = parse_decimal(request.args.get("saldo_min"))
    saldo_max = parse_decimal(request.args.get("saldo_max"))
    fecha_inicio = parse_date(request.args.get("fecha_inicio"))
    fecha_fin = parse_date(request.args.get("fecha_fin"))
    limit, offset = parse_limit_offset(request.args)

    historial = search_alumnos_audit(
        nombre=nombre, email=email, operation=operation,
        saldo_min=saldo_min, saldo_max=saldo_max,
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
        limit=limit, offset=offset,
    )
    return render_template(
        "auditoria_alumnos.html",
        auditoria=historial,
        busqueda=True,
        params=request.args,
        limit=limit,
        offset=offset,
    )

@alumnos_bp.route("/add", methods=["POST"])
def add():
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    saldo_str = request.form.get("saldo", "0")
    try:
        saldo = float(saldo_str)
    except ValueError:
        saldo = 0.0
    if nombre and email:
        insert_alumno(nombre, email, saldo)
    return redirect(url_for("alumnos.list_"))

@alumnos_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        saldo_str = request.form.get("saldo", "0")
        try:
            saldo = float(saldo_str)
        except ValueError:
            saldo = 0.0
        if nombre and email:
            update_alumno(id, nombre, email, saldo)
        return redirect(url_for("alumnos.list_"))
    
    alumno = get_alumno(id)
    if not alumno:
        return redirect(url_for("alumnos.list_"))
    return render_template("alumnos_edit.html", alumno=alumno)

@alumnos_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    delete_alumno(id)
    return redirect(url_for("alumnos.list_"))