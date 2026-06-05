"""
Punto de entrada de la aplicación (Application Factory).

- create_app() construye la instancia de Flask y registra blueprints y errores.
- Sin lógica de negocio: solo configuración y ensamblado.

Ejecución:
    export FLASK_APP=app.py
    flask run
"""
from __future__ import annotations

from flask import Flask, render_template

from routes import main_bp, alumnos_bp, profesores_bp, asignaturas_bp, matriculas_bp, olap_bp


def create_app() -> Flask:
    """Crea y configura la aplicación Flask (patrón factory)."""
    app = Flask(__name__)

    # Configuración mínima (evitar hardcodear en código)
    app.config["ENV"] = "development"
    app.config["SECRET_KEY"] = "dev-change-in-production"

    # Blueprints por recurso
    app.register_blueprint(main_bp)
    app.register_blueprint(alumnos_bp)
    app.register_blueprint(profesores_bp)
    app.register_blueprint(asignaturas_bp)
    app.register_blueprint(matriculas_bp)
    app.register_blueprint(olap_bp)

    # Páginas de error (misma base que el resto)
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app


# Instancia única para flask run y servidores WSGI
app = create_app()