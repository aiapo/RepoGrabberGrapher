from flask import Blueprint
from app.core.routes.api.repositories import repositories_route
from app.core.routes.api.refactorings import refactorings_route

api = Blueprint('api', __name__, template_folder='templates', url_prefix='/api')

api.register_blueprint(repositories_route)
api.register_blueprint(refactorings_route)