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
import requests

"""
Register the Flask app and import the routes (the API route has it's own blueprint)
"""
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

"""
Initialize the SQLite Database
"""
DB_NAME = "rgg.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DB_NAME
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        """
        Create all the relations in the database and disable journal mode, for speedups
        """
        db.create_all()
        db.session.execute(sqlalchemy.text('PRAGMA journal_mode = OFF'))

        """
        Parse the command line arguments, and if there's a RGDS file to be imported process it
        """
        opts = parseArgs(sys.argv[1:])

        if opts.rgds:
            url = opts.rgds

            """
            Read in and import the dataset only if it hasn't been imported yet
            """
            def importDs(ds):
                if(readRGDS(ds,True,DB_NAME)):
                    print("Dataset successfully imported into database from RGDS file!")
                else:
                    print("Dataset ignored because RGDS file has already been imported. Using database...") 

            """
            Check to make sure that the argument passed is a local file or a remote file
            """
            if(validators.url(url)):
                print("Remote file detected, downloading...")
                domain = urlparse(url).netloc

                """
                Unfurl DOI records to get the current URL
                """
                if domain == 'doi.org':
                    r = requests.head(url, allow_redirects=True)
                    url = r.url
                    domain = urlparse(url).netloc

                """
                Go through all the Downloaders installed and if it supports the remote URL
                then use it, otherwise if no Downloader supports it, just use the Generic.

                D/N: Genuinely I have no idea if this is an appropriate way of doing this
                sort of thing, it seems kind of sketchy to me, it literally has to import
                each any every Downloader for the base class to know and then initalize it.
                """
                dl = None
                foundDl = False
                genericDl = None

                """
                Iterate through all the Downloaders (the base class knows all it's children,
                so we iterate that way)
                """
                for d in Downloader.plugins:
                    dl = d()
                    if(dl.NAME=='Generic'):
                        genericDl = dl
                    if domain in dl.BASEDOMAINS:
                        foundDl = True
                        break

                """
                Double check that neither is still None, would indicate that there's no
                Downloaders
                """
                if(dl != None and genericDl != None):
                    if (not foundDl):
                        print(domain+" doesn't have it's own Downloader, using Generic...")
                        dl = genericDl
                    else:
                        print("Found a downloader for "+domain+"...") 

                    """
                    Download using the Downloader and import, then delete when done
                    """
                    path = os.path.dirname(os.path.abspath(__file__))+"/ds.rgds"
                    datasets = []
                    if(dl.checkExists(url)):
                        if(dl.checkDir(url)):
                            yamlFile = dl.getYamlUrl(url)
                            datasets = dl.readYaml(yamlFile)
                        else:
                            datasets.append({
                                "location": ""
                            })    
                        print(datasets)
                        for dataset in datasets:
                            dl.download(dl.getDownloadUrl(url,dataset['location']),path)             
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

    """
    Open the browser to the application, and start the web app
    """            
    webbrowser.open('http://localhost:8000')
    app.run(debug=False, port=8000)