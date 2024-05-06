import sys
from flask import Flask,render_template
import webbrowser
import sqlalchemy
import validators
import os
from app.core.downloader import (
    Downloader
)
from urllib.parse import urlparse
from app.db.models import db
from app.core.functions import (
    parseArgs,
    readRGDS
)
from app.core.routes.api.main import api

app = Flask(__name__)
app.register_blueprint(api)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/repositories')
def repositories():
    return render_template('repositories.html')

@app.route('/refactorings')
def refactorings():
    return render_template('refactorings.html')

DB_NAME = "rgg.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DB_NAME
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        db.session.execute(sqlalchemy.text('PRAGMA journal_mode = OFF'))

        opts = parseArgs(sys.argv[1:])

        if opts.rgds:
            url = opts.rgds
            def importDs(ds):
                if(readRGDS(ds,True,DB_NAME)):
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