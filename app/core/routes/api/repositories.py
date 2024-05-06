import pandas as pd
from flask import Blueprint
import sqlalchemy
import hashlib
from app.db.models import (
    Queries,
    Repositories
)
from app.db.db import db
from app.core.functions import (
    binnedDataCSV
)

repositories_route = Blueprint('repositories', __name__, template_folder='templates', url_prefix='/repos')

@repositories_route.route('list')
def reposList():
    hash=hashlib.md5(("reposList").encode()).hexdigest()
    result = db.session.query(Queries.result).filter_by(hash=hash).one_or_none()
    if(result != None):
        return result[0]
    else:
        repos = []
        for row in Repositories.query.all():
            repos.append(Repositories.as_dict(row))
        json = pd.DataFrame(repos, columns=['id','name','owner','url','description','primarylanguage','creationdate','updatedate','pushdate','isarchived','archivedat','isforked','isempty','islocked','isdisabled','istemplate','totalissueusers','totalmentionableusers','totalcommittercount','totalprojectsize','totalcommits','issuecount','forkcount','starcount','watchcount','branchname','domain']).to_json(orient='records')
    
        r = "{\"data\":"+json+"}"
        db.session.add(Queries(hash=hash,result=r))
        db.session.commit()
        return r

@repositories_route.route('countBy/<string:countBy>')
def reposBy(countBy):
    hash=hashlib.md5(("reposBy"+countBy).encode()).hexdigest()
    result = db.session.query(Queries.result).filter_by(hash=hash).one_or_none()
    if(result != None):
        return result[0]
    else:
        if countBy=="creation":
            results = [tuple(row) for row in db.session.query(sqlalchemy.func.strftime('%Y', Repositories.creationDate), sqlalchemy.func.count(sqlalchemy.func.strftime('%Y', Repositories.creationDate))).group_by(sqlalchemy.func.strftime('%Y', Repositories.creationDate)).all()]
            r = pd.DataFrame(results, columns=['year', 'count']).to_json(orient='records')
        elif countBy=="push":
            results = [tuple(row) for row in db.session.query(sqlalchemy.func.strftime('%Y', Repositories.pushDate), sqlalchemy.func.count(sqlalchemy.func.strftime('%Y', Repositories.pushDate))).group_by(sqlalchemy.func.strftime('%Y', Repositories.pushDate)).all()]
            r = pd.DataFrame(results, columns=['year', 'count']).to_json(orient='records')
        elif countBy=="update":
            results = [tuple(row) for row in db.session.query(sqlalchemy.func.strftime('%Y', Repositories.updateDate), sqlalchemy.func.count(sqlalchemy.func.strftime('%Y', Repositories.updateDate))).group_by(sqlalchemy.func.strftime('%Y', Repositories.updateDate)).all()]
            r = pd.DataFrame(results, columns=['year', 'count']).to_json(orient='records')
        elif countBy=="domain":
            results = [tuple(row) for row in db.session.query(Repositories.domain, sqlalchemy.func.count(Repositories.domain)).group_by(Repositories.domain).all()]
            r = pd.DataFrame(results, columns=['domain', 'count']).to_json(orient='records')
        else:
            return '{"status":"error","message":"Invalid countBy.. Try again."}'
    
        db.session.add(Queries(hash=hash,result=r))
        db.session.commit()
        return r

@repositories_route.route('countBy/<string:countBy>/binCount/<int:binCount>')
def reposBinned(countBy,binCount):
    if countBy=="commit":
        return binnedDataCSV('totalCommits',binCount)  
    
    if countBy=="committer":
        return binnedDataCSV('totalCommitterCount',binCount)  
    
    if countBy=="size":
        return binnedDataCSV('totalProjectSize',binCount)  
        
    if countBy=="issue":
        return binnedDataCSV('issueCount',binCount)  
        
    if countBy=="watch":
        return binnedDataCSV('watchCount',binCount)  
        
    if countBy=="star":
        return binnedDataCSV('starCount',binCount)  
        
    return '{"status":"error","message":"Invalid countBy or binCount.. Try again."}'