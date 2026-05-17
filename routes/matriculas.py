"""Rutas del recurso matriculas."""
from __future__ import annotations

from flask import Blueprint, render_template

from models.db import get_matriculas

matriculas_bp = Blueprint("matriculas", __name__, url_prefix="/matriculas")


@matriculas_bp.route("")
def list_():
    matriculas = get_matriculas()
    return render_template("matriculas.html", matriculas=matriculas)