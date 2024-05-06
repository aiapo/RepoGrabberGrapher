import argparse
import sys
import pandas as pd
import numpy as np
from flask import Flask, render_template
import webbrowser
import gzip
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import hashlib
import re
from dataclasses import dataclass
import validators
import requests
from tqdm import tqdm
from sqlalchemy.dialects.sqlite import insert
import os
from zlib_ng import gzip_ng_threaded
import sqlite3
from app.core.downloader import (
    Downloader
)
from urllib.parse import urlparse
import os
import traceback
from importlib import util


app = Flask(__name__)
DB_NAME = "rgg.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DB_NAME
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Imports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Import {self.hash}>'
    
class Queries(db.Model):
    hash = db.Column(db.Text, primary_key=True)
    result = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'{self.result}'
    
@dataclass    
class Repositories(db.Model):
    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    owner = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    primaryLanguage = db.Column(db.Text, nullable=False)
    creationDate = db.Column(db.Text, nullable=False)
    updateDate = db.Column(db.Text, nullable=False)
    pushDate = db.Column(db.Text, nullable=False)
    isArchived = db.Column(db.Boolean, nullable=False)
    archivedAt = db.Column(db.Text, nullable=True)
    isForked = db.Column(db.Boolean, nullable=False)
    isEmpty = db.Column(db.Text, nullable=False)
    isLocked = db.Column(db.Text, nullable=False)
    isDisabled = db.Column(db.Text, nullable=False)
    isTemplate = db.Column(db.Text, nullable=False)
    totalIssueUsers = db.Column(db.Integer, nullable=False)
    totalMentionableUsers = db.Column(db.Integer, nullable=False)
    totalCommitterCount = db.Column(db.Integer, nullable=False)
    totalProjectSize = db.Column(db.Integer, nullable=False)
    totalCommits = db.Column(db.Integer, nullable=False)
    issueCount = db.Column(db.Integer, nullable=False)
    forkCount = db.Column(db.Integer, nullable=False)
    starCount = db.Column(db.Integer, nullable=False)
    watchCount = db.Column(db.Integer, nullable=False)
    branchName = db.Column(db.Text, nullable=False)
    domain = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Repository {self.name}>'
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

@dataclass    
class Languages(db.Model):
    repoId = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, primary_key=True)
    size = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Language {self.repoId}:{self.name}>'
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

@dataclass    
class Refactorings(db.Model):
    refactoringHash = db.Column(db.Text, primary_key=True,)
    commit = db.Column(db.Text, primary_key=True)
    gituri = db.Column(db.Text)
    repositoryId = db.Column(db.Text, primary_key=True)
    refactoringName = db.Column(db.Text, primary_key=True)
    leftStartLine = db.Column(db.Text)
    leftEndLine = db.Column(db.Text)
    leftStartColumn = db.Column(db.Text)
    leftEndColumn = db.Column(db.Text)
    leftFilePath = db.Column(db.Text)
    leftCodeElementType = db.Column(db.Text)
    leftDescription = db.Column(db.Text)
    leftCodeElement = db.Column(db.Text)
    rightStartLine = db.Column(db.Text)
    rightEndLine = db.Column(db.Text)
    rightStartColumn = db.Column(db.Text)
    rightEndColumn = db.Column(db.Text)
    rightFilePath = db.Column(db.Text)
    rightCodeElementType = db.Column(db.Text)
    rightDescription = db.Column(db.Text)
    rightCodeElement = db.Column(db.Text)
    commitAuthor = db.Column(db.Text)
    commitMessage = db.Column(db.Text)
    commitDate = db.Column(db.Text)

    def __repr__(self):
        return f'<Refactoring {self.refactoringHash}>'
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def parseBool(inp):
    return inp.lower=='t'

def db_init():
    db.create_all()
    db.session.execute(sqlalchemy.text('PRAGMA journal_mode = OFF'))

def sendToDBCore(rows,conn: sqlite3.Connection):
    if rows:
        if any(d['relation'] == 'repositories' for d in rows):
            conn.executemany('INSERT INTO repositories VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT DO NOTHING', [
                (
                    x['data'][0],x['data'][1],x['data'][2],x['data'][3],x['data'][4],
                    x['data'][5],x['data'][6],x['data'][7],x['data'][8],parseBool(x['data'][9]),
                    x['data'][10],parseBool(x['data'][11]),parseBool(x['data'][12]),
                    parseBool(x['data'][13]),parseBool(x['data'][14]),parseBool(x['data'][15]),
                    int(x['data'][16]),int(x['data'][17]),int(x['data'][18]),int(x['data'][19]),
                    int(x['data'][20]),int(x['data'][21]),int(x['data'][22]),int(x['data'][23]),
                    int(x['data'][24]),x['data'][25],x['data'][26]
                ) for x in rows if x['relation'] == 'repositories']
            )
            
        if any(d['relation'] == 'languages' for d in rows):
            conn.executemany('INSERT INTO languages VALUES (?,?,?) ON CONFLICT DO NOTHING', [
                (
                    x['data'][0],x['data'][1],int(x['data'][2])
                ) for x in rows if x['relation'] == 'languages']
            )
            
        if any(d['relation'] == 'refactorings' for d in rows):
            conn.executemany('INSERT INTO refactorings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT DO NOTHING', [
                (
                    x['data'][0],x['data'][1],x['data'][2],x['data'][3],x['data'][4],
                    int(x['data'][5]),int(x['data'][6]),int(x['data'][7]),int(x['data'][8]),
                    x['data'][9],x['data'][10],x['data'][11],x['data'][12],int(x['data'][13]),
                    int(x['data'][14]),int(x['data'][15]),int(x['data'][16]),x['data'][17],
                    x['data'][18],x['data'][19],x['data'][20],x['data'][21],x['data'][22],
                    x['data'][23]
                ) for x in rows if x['relation'] == 'refactorings']
            )

        conn.commit()    

def initApi():
    types = ["all","mobile","desktop","web"]
    count = ["year","type"]

    print("Running some pre-analysis...")
    pbar = tqdm(total=(len(types)*len(count)))
    for x in types:
        for y in count:
            refactoringsBy(x,y)
            pbar.update(1)
    pbar.close()       

def readRGDS(fileName,compressed):
    conn = sqlite3.connect("instance/"+DB_NAME, isolation_level=None)

    conn.execute('PRAGMA journal_mode = OFF;')
    conn.execute('PRAGMA synchronous = 0;')

    validAction = {
        "rgds_version":2,
        "title":2,
        "relation":2,
        "attribute":3,
        "data":1
    }
    if(compressed):
        totalLines = sum (1 for line in gzip_ng_threaded.open(fileName,'rt', encoding="utf8"))

        with gzip_ng_threaded.open(fileName,'rt', encoding="utf8") as f:
            m = hashlib.md5()
            while True:
                data = f.read(16384).encode('utf-8')
                if not data:
                    break
                m.update(data)
            hashI = m.hexdigest()

            if(Imports.query.filter_by(hash=hashI).all()):
                initApi()
                return False
            
        with gzip_ng_threaded.open(fileName,'rt', encoding="utf8") as f:
            currentRelation = ''
            startDataRead = False
            step = 0
            rows = [] 

            for line in tqdm(f, total=totalLines):
                if step % 1000000 == 0 or step==totalLines-1:
                    sendToDBCore(rows,conn)
                    rows.clear()

                line = line.strip("\n")
                if not line.lstrip().startswith('%'):  
                    if(line.startswith('@')):
                        currentActionFull = re.split(r' (?=(?:[^"]*"[^"]*")*[^"]*$)', line[1:].lower())
                        currentAction = currentActionFull[0].lower()
                        if(validAction.get(currentAction) != None):
                            if(validAction.get(currentAction)==len(currentActionFull)):
                                startDataRead = False
                                if(currentAction=='relation'):
                                    currentRelation = currentActionFull[1]
                                elif(currentAction=='data'):
                                    startDataRead = True
                            else:
                                print('[ERROR] Invalid number of parameters for @Action '+currentAction+' in RGDS file... ignoring')
                        else:
                            print('[ERROR] Invalid @Action '+currentAction+' in RGDS file... ignoring')
                    elif(startDataRead and line!=''):
                        currentDataLine = re.split('","',line)

                        for i in range(len(currentDataLine)):
                            currentDataLine[i] = re.sub(r'^"|"$','',currentDataLine[i])

                        rows.append({"relation": currentRelation,"data": currentDataLine})            
                step+=1

            sendToDBCore(rows,conn)
            rows.clear()

            db.session.add(Imports(hash=hashI))
            db.session.commit()

            conn.close()

            initApi()

            return True    
    else:
        print("[ERROR] Only compressed RGDS is supported at this time.")
        return False  

def parseArgs(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--rgds', help='Load Repository Dataset from RGDS File', required=True)

    if len(argv) == 0:
        parser.print_help()
        exit(1)
    opts = parser.parse_args(argv)
    return opts

def binnedDataCSV(column,binSize):
    hash=hashlib.md5(("binnedDataCSV"+column+str(binSize)).encode()).hexdigest()
    result = db.session.query(Queries.result).filter_by(hash=hash).one_or_none()
    if(result != None):
        return result[0]
    else:
        repos = []
        for row in Repositories.query.all():
            repos.append(Repositories.as_dict(row))
        df = pd.DataFrame(repos)

        # repositories/commits
        bmin = df[column].min()
        bmax = df[column].max()

        # specify the number of desired cuts here
        bins = np.linspace(bmin, bmax, num=binSize+1).astype(int)
        labels = [f'({bins[i]}, {bins[i+1]}]' for i in range(binSize)]
        binned = pd.cut(df[column],bins,labels=labels)
        
        r = binned.groupby([binned]).count().to_json()
        db.session.add(Queries(hash=hash,result=r))
        db.session.commit()

        return r
    
@app.route('/api/repos/list')
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

@app.route('/api/repos/countBy/<string:countBy>')
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

@app.route('/api/repos/countBy/<string:countBy>/binCount/<int:binCount>')
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

@app.route('/api/refactorings/groupBy/<string:groupBy>/countBy/<string:countBy>')
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/repositories')
def repositories():
    return render_template('repositories.html')

@app.route('/refactorings')
def refactorings():
    return render_template('refactorings.html')

if __name__ == '__main__':
    with app.app_context():
        db_init()

        opts = parseArgs(sys.argv[1:])

        if opts.rgds:
            url = opts.rgds
            def importDs(ds):
                if(readRGDS(ds,True)):
                    print("Dataset successfully imported into database from RGDS file!")
                else:
                    print("Dataset ignored because RGDS file has already been imported. Using database...") 

            if(validators.url(url)):
                print("Remote file detected, downloading...")
                domain = urlparse(url).netloc
                dl = None
                foundDl = False
                genericDl = None
                for d in Downloader.plugins:
                    dl = d()
                    if(dl.NAME=='Generic'):
                        genericDl = dl
                    if domain in dl.BASEDOMAINS:
                        foundDl = True
                        break

                if(dl != None and genericDl != None):
                    if (not foundDl):
                        print(domain+" doesn't have it's own Downloader, using Generic...")
                        dl = genericDl
                    else:
                        print("Found a downloader for "+domain+"...")    

                    path = os.path.dirname(os.path.abspath(__file__))+"/ds.rgds"
                    dUrl = dl.getDownloadUrl(url)
                    dl.download(dUrl,path)             
                    importDs(path)
                    print("Deleting temporary download...")
                    if os.path.exists(path):
                        os.remove(path)
                else:
                    print("No downloaders found, not even the generic. Check your files.")
                    exit(1)          
            else:
                print("Local file detected...")
                importDs(opts.rgds)    
                
    webbrowser.open('http://localhost:8000')
    app.run(debug=False, port=8000)