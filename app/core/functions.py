import sqlite3
import argparse
from tqdm import tqdm
from zlib_ng import gzip_ng_threaded
import pandas as pd
import numpy as np
import hashlib
import re
from app.db.models import (
    Imports,
    Queries,
    Repositories
)
from app.core.routes.api.refactorings import (
    refactoringsBy
)
from app.db.db import db

"""
parseBool:

Simple bool parser because RGDS uses t/f for boolean values

:param inp(str): Input string

:return bool: Boolean based on input
"""
def parseBool(inp:str):
    return inp.lower=='t'

"""
sendToDBCore:

Uses a direct SQLite connection to insert in bulk

:param rows(list[dict{relation,data}]): Takes a list of dictonaries
 comprising of the relation and the data
:param conn(sqlite3.Connection): Takes a SQLite3 connection
"""
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


"""
initApi:

Does preprocessing (on a large dataset, this is needed so that the pages get rendered quickly)
Specifically for refactorings.
"""
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


"""
readRGDS:

Reads in a RGDS file and imports it into the database, line by line
NOTE: Only compressed RGDS files are supported as of this time.

:param fileName(str): Path of the RGDS file
:param compressed(bool): If the RGDS file is compressed
:param db_name(str): Name of the database file (needed for speedy import)

:return bool: If the the import was a success
"""
def readRGDS(fileName:str,compressed:bool,db_name:str):
    conn = sqlite3.connect("instance/"+db_name, isolation_level=None)

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

            if(db.session.query(Imports).filter_by(hash=hashI).one_or_none() != None):
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

"""
parseArgs:

Uses argparse to parse arguments and verify only supported commands used

:param argv(list(str)): List of arguments

:return opts: Valid arguments and their data
"""
def parseArgs(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--rgds', help='Load Repository Dataset from RGDS File', required=True)

    if len(argv) == 0:
        parser.print_help()
        exit(1)
    opts = parser.parse_args(argv)
    return opts


"""
binnedDataCSV:

Bin data for use in histograms based on a specific size
Specifically for Repositories as of now

:param column(str): Specified column to do the binning on
:param binSize(int): Size of each bin

:return str: JSON formatted bins with counts
"""
def binnedDataCSV(column:str,binSize:int):
    hash=hashlib.md5(("binnedDataCSV"+column+str(binSize)).encode()).hexdigest()
    result = db.session.query(Queries.result).filter_by(hash=hash).one_or_none()
    if(result != None):
        return result[0]
    else:
        repos = []
        for row in db.session.query(Repositories).all():
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
