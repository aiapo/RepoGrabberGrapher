from flask import Blueprint
from app.core.routes.api.repositories import repositories_route
from app.core.routes.api.refactorings import refactorings_route

"""
Create API blueprint
"""
api = Blueprint("api", __name__, template_folder="templates", url_prefix="/api")

"""
Register repositories and refactorings blueprints to the API
"""
api.register_blueprint(repositories_route)
api.register_blueprint(refactorings_route)
