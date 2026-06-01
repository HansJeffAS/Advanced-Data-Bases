"""Rutas del recurso profesor."""
from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for

from models.db import (
    get_profesores, insert_profesor, update_profesor, delete_profesor, get_profesor,
    search_profesores, search_profesores_audit,
)
from tools.parse_params import parse_str, parse_date, parse_limit_offset

profesores_bp = Blueprint("profesores", __name__, url_prefix="/profesores")

@profesores_bp.route("")
def list_():
    profesores = get_profesores()
    return render_template("profesores.html", profesores=profesores)

@profesores_bp.route("/buscar")
def buscar():
    nombre = parse_str(request.args.get("nombre"))
    email = parse_str(request.args.get("email"))
    limit, offset = parse_limit_offset(request.args)

    profesores = search_profesores(
        nombre=nombre, email=email,
        limit=limit, offset=offset,
    )
    return render_template(
        "profesores.html",
        profesores=profesores,
        busqueda=True,
        params=request.args,
        limit=limit,
        offset=offset,
    )


@profesores_bp.route("/auditoria/buscar")
def auditoria_buscar():
    nombre = parse_str(request.args.get("nombre"))
    email = parse_str(request.args.get("email"))
    operation = parse_str(request.args.get("operation"))
    fecha_inicio = parse_date(request.args.get("fecha_inicio"))
    fecha_fin = parse_date(request.args.get("fecha_fin"))
    limit, offset = parse_limit_offset(request.args)

    historial = search_profesores_audit(
        nombre=nombre, email=email, operation=operation,
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
        limit=limit, offset=offset,
    )
    return render_template(
        "auditoria_profesores.html",
        auditoria=historial,
        busqueda=True,
        params=request.args,
        limit=limit,
        offset=offset,
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