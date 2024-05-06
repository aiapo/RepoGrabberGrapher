import pandas as pd
from flask import Blueprint
import sqlalchemy
import hashlib
from app.db.models import (
    Queries,
    Repositories,
    Refactorings
)
from app.db.db import db

refactorings_route = Blueprint('refactorings', __name__, template_folder='templates', url_prefix='/refactorings')

@refactorings_route.route('/groupBy/<string:groupBy>/countBy/<string:countBy>')
def refactoringsBy(groupBy,countBy):
    hash=hashlib.md5(("refactoringsBy"+groupBy+countBy).encode()).hexdigest()
    result = db.session.query(Queries.result).filter_by(hash=hash).one_or_none()
    if(result != None):
        return result[0]
    else:
        if groupBy=="all":
            if countBy=="year":
                results = [tuple(row) for row in db.session.query(sqlalchemy.func.strftime('%Y', Refactorings.commitDate), sqlalchemy.func.count(sqlalchemy.func.strftime('%Y', Refactorings.commitDate))).group_by(sqlalchemy.func.strftime('%Y', Refactorings.commitDate)).all()]
                r = pd.DataFrame(results, columns=['year', 'count']).to_json(orient='records')
            elif countBy=="type":
                results = [tuple(row) for row in db.session.query(Refactorings.refactoringName, sqlalchemy.func.count(Refactorings.refactoringName)).group_by(Refactorings.refactoringName).all()]
                r = pd.DataFrame(results, columns=['type', 'count']).to_json(orient='records')

        elif groupBy=="desktop":
            if countBy=="year":
                results = [tuple(row) for row in db.session.query(sqlalchemy.func.strftime('%Y', Refactorings.commitDate),sqlalchemy.func.count(sqlalchemy.func.strftime('%Y', Refactorings.commitDate))).filter(Repositories.domain=='desktop').join(Repositories,Repositories.id==Refactorings.repositoryId).group_by(sqlalchemy.func.strftime('%Y', Refactorings.commitDate)).all()]
                r = pd.DataFrame(results, columns=['year', 'count']).to_json(orient='records')
            elif countBy=="type":
                results = [tuple(row) for row in db.session.query(Refactorings.refactoringName, sqlalchemy.func.count(Refactorings.refactoringName)).filter(Repositories.domain=='desktop').join(Repositories,Repositories.id==Refactorings.repositoryId).group_by(Refactorings.refactoringName).all()]
                r = pd.DataFrame(results, columns=['type', 'count']).to_json(orient='records')
            
        elif groupBy=="mobile":
            if countBy=="year":
                results = [tuple(row) for row in db.session.query(sqlalchemy.func.strftime('%Y', Refactorings.commitDate),sqlalchemy.func.count(sqlalchemy.func.strftime('%Y', Refactorings.commitDate))).filter(Repositories.domain=='mobile').join(Repositories,Repositories.id==Refactorings.repositoryId).group_by(sqlalchemy.func.strftime('%Y', Refactorings.commitDate)).all()]
                r = pd.DataFrame(results, columns=['year', 'count']).to_json(orient='records')
            elif countBy=="type":
                results = [tuple(row) for row in db.session.query(Refactorings.refactoringName, sqlalchemy.func.count(Refactorings.refactoringName)).filter(Repositories.domain=='mobile').join(Repositories,Repositories.id==Refactorings.repositoryId).group_by(Refactorings.refactoringName).all()]
                r = pd.DataFrame(results, columns=['type', 'count']).to_json(orient='records')
            
        elif groupBy=="web":
            if countBy=="year":
                results = [tuple(row) for row in db.session.query(sqlalchemy.func.strftime('%Y', Refactorings.commitDate),sqlalchemy.func.count(sqlalchemy.func.strftime('%Y', Refactorings.commitDate))).filter(Repositories.domain=='web').join(Repositories,Repositories.id==Refactorings.repositoryId).group_by(sqlalchemy.func.strftime('%Y', Refactorings.commitDate)).all()]
                r = pd.DataFrame(results, columns=['year', 'count']).to_json(orient='records')
            elif countBy=="type":
                results = [tuple(row) for row in db.session.query(Refactorings.refactoringName, sqlalchemy.func.count(Refactorings.refactoringName)).filter(Repositories.domain=='web').join(Repositories,Repositories.id==Refactorings.repositoryId).group_by(Refactorings.refactoringName).all()]
                r = pd.DataFrame(results, columns=['type', 'count']).to_json(orient='records')
        else:    
            return '{"status":"error","message":"Invalid groupBy or countBy.. Try again."}'
    
        db.session.add(Queries(hash=hash,result=r))
        db.session.commit()
        return r