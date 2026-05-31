"""Rutas del recurso matriculas."""
from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from models.db import get_matriculas, get_alumnos, get_asignaturas, matricular_alumno_transaccional, get_alumno, get_asignatura

matriculas_bp = Blueprint("matriculas", __name__, url_prefix="/matriculas")


@matriculas_bp.route("")
def list_():
    matriculas = get_matriculas()
    alumnos = get_alumnos()
    asignaturas = get_asignaturas()
    resultado = request.args.get("resultado")
    return render_template(
        "matriculas.html",
        matriculas=matriculas,
        alumnos=alumnos,
        asignaturas=asignaturas,
        resultado=resultado,
    )

@matriculas_bp.route("/matricular", methods=["POST"])
def matricular():
    alumno_id_str = request.form.get("alumno_id")
    asignatura_id_str = request.form.get("asignatura_id")

    if not alumno_id_str or not asignatura_id_str:
        return redirect(url_for("matriculas.list_"))

    try:
        alumno_id = int(alumno_id_str)
        asignatura_id = int(asignatura_id_str)
    except ValueError:
        return redirect(url_for("matriculas.list_"))

    resultado = matricular_alumno_transaccional(alumno_id, asignatura_id)

    matriculas = get_matriculas()
    alumnos = get_alumnos()
    asignaturas = get_asignaturas()

    return render_template(
        "matriculas.html",
        matriculas=matriculas,
        alumnos=alumnos,
        asignaturas=asignaturas,
        resultado=resultado,
        alumno_sel=alumno_id,
        asignatura_sel=asignatura_id,
    )

@matriculas_bp.route("/preview")
def preview():
    """Devuelve JSON con datos del alumno y asignatura para el preview dinámico."""
    alumno_id_str = request.args.get("alumno_id")
    asignatura_id_str = request.args.get("asignatura_id")

    data = {}

    if alumno_id_str and alumno_id_str.isdigit():
        alumno = get_alumno(int(alumno_id_str))
        if alumno:
            data["alumno_nombre"] = alumno.nombre
            data["alumno_saldo"] = float(alumno.saldo)

    if asignatura_id_str and asignatura_id_str.isdigit():
        asignatura = get_asignatura(int(asignatura_id_str))
        if asignatura:
            data["asignatura_nombre"] = asignatura.nombre
            data["asignatura_precio"] = float(asignatura.precio)
            data["asignatura_max"] = asignatura.max_alumnos

    return jsonify(data)