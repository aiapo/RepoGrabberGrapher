import argparse
import sys
import dask as dd
import dask.dataframe as ddf
import pandas as pd
import numpy as np
from flask import Flask, render_template
from dask.diagnostics import ProgressBar
from dask_sql import Context
from dask.cache import Cache
import webbrowser

app = Flask(__name__)
dd.config.set({"dataframe.convert-string": False})
cache = Cache(2e9)  # Leverage two gigabytes of memory
cache.register()    # Turn cache on globally

repoCSVLocation = ''
refactorCSVLocation = ''

# create the context db
c = Context()

def parseArgs(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--repositorycsv', help='Load Repository Dataset from CSV File/URL', required=True)
    parser.add_argument('--refactoringcsv', help='Load Refactoring Dataset from CSV File/URL', required=True)

    if len(argv) == 0:
        parser.print_help()
        exit(1)
    opts = parser.parse_args(argv)
    return opts

def binnedDataCSV(column,binSize):
    with ProgressBar():
        # repositories/commits
        bmin, bmax = dd.compute(reposDf[column].min(), reposDf[column].max())

        # specify the number of desired cuts here
        bins = np.linspace(bmin, bmax, num=binSize+1).astype(int)
        labels = [f'({bins[i]}, {bins[i+1]}]' for i in range(binSize)]
        binned = reposDf[column].map_partitions(pd.cut,bins,labels=labels).compute()

        return binned.groupby([binned]).count().to_json()  
    
def countedByDataCSV(db,by,column):
        if by=='year':
            select = "EXTRACT (YEAR FROM "+column+") year"
        elif by =='type':
            select = column+" type"
        else:
            return '{"status":"error","message":"Invalid groupBy or countBy.. Try again."}'
        
        with ProgressBar():
            return c.sql("SELECT 1 count, "+select+" FROM "+db).compute().groupby(by).count().to_json()
        
def countedByDataJoinedCSV(column,by,domain):
        if by=='year':
            select = "EXTRACT (YEAR FROM "+column+") year"
        elif by =='type':
            select = column+" type"
        else:
            return '{"status":"error","message":"Invalid groupBy or countBy.. Try again."}'

        with ProgressBar():
            return c.sql("SELECT 1 count, "+select+" FROM refactor LEFT JOIN repos ON refactor.repositoryid=repos.id WHERE repos.domain='"+domain+"'").compute().groupby(by).count().to_json()
        
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
    opts = parseArgs(sys.argv[1:])

    if opts.repositorycsv:
        repoCSVLocation=opts.repositorycsv

    if opts.refactoringcsv:
        refactorCSVLocation=opts.refactoringcsv    

    @app.route('/api/repos/list')
    def reposList():
        # repositories listed
            with ProgressBar():
                json = reposDf.compute().to_json(orient ='records')
                return "{\"data\":"+json+"}"

    @app.route('/api/repos/countBy/<string:countBy>')
    def reposBy(countBy):
        if countBy=="creation":
            return countedByDataCSV('repos','year','creationdate')
        
        if countBy=="push":
            return countedByDataCSV('repos','year','pushdate')
        
        if countBy=="update":
            return countedByDataCSV('repos','year','updatedate')
        
        if countBy=="domain":
            with ProgressBar():
                return c.sql("SELECT 1 count, domain FROM repos").compute().groupby(['domain']).count().to_json()
    
        return '{"status":"error","message":"Invalid countBy.. Try again."}'
    
    @app.route('/api/repos/countBy/<string:countBy>/binCount/<int:binCount>')
    def reposBinned(countBy,binCount):
        if countBy=="commit":
            return binnedDataCSV('totalcommits',binCount)  
        
        if countBy=="committer":
            return binnedDataCSV('totalcommittercount',binCount)  
        
        if countBy=="size":
            return binnedDataCSV('totalprojectsize',binCount)  
            
        if countBy=="issue":
            return binnedDataCSV('issuecount',binCount)  
            
        if countBy=="watch":
            return binnedDataCSV('watchcount',binCount)  
            
        if countBy=="star":
            return binnedDataCSV('starcount',binCount)  
            
        return '{"status":"error","message":"Invalid countBy or binCount.. Try again."}'
    
    @app.route('/api/refactorings/groupBy/<string:groupBy>/countBy/<string:countBy>')
    def refactoringsBy(groupBy,countBy):
        if groupBy=="all":
            if countBy=="year":
                return countedByDataCSV('refactor','year','commitdate')
            
            if countBy=="type":
                return countedByDataCSV('refactor','type','refactoringname')

        if groupBy=="desktop":
            if countBy=="year":
                return countedByDataJoinedCSV('commitdate','year','desktop')
            
            if countBy=="type":
                return countedByDataJoinedCSV('refactoringname','type','desktop')

        if groupBy=="mobile":
            if countBy=="year":
                return countedByDataJoinedCSV('commitdate','year','mobile')
            
            if countBy=="type":
                return countedByDataJoinedCSV('refactoringname','type','mobile')
        
        if groupBy=="web":
            if countBy=="year":
                return countedByDataJoinedCSV('commitdate','year','web')
            
            if countBy=="type":
                return countedByDataJoinedCSV('refactoringname','type','web')
        
        return '{"status":"error","message":"Invalid groupBy or countBy.. Try again."}'

    reposDf = ddf.read_csv(repoCSVLocation, 
            dtype={'archivedat': 'object'},
            parse_dates=['creationdate','updatedate','pushdate','archivedat']
        ) 
    
    refactorDf = ddf.read_csv(refactorCSVLocation,
        parse_dates=['commitdate']
    ) 
    
    # create the "db"s
    c.create_table("repos", reposDf)
    c.create_table("refactor", refactorDf)

    webbrowser.open('http://localhost:8000')
    app.run(debug=False, port=8000)