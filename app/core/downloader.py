import requests
import tqdm
from abc import ABCMeta, abstractmethod
import os
import traceback
from importlib import util
import yaml

class Downloader(metaclass=ABCMeta):
    ## Abstract Fields ##
    NAME: str = 'Base' # Name of this downloader
    BASEDOMAINS: tuple[str, ...] = () # List of domains that use this downloader

    plugins = []

    def __int__(self):
        baseDomains = self.baseDomains
        print(baseDomains)

    # For every class that inherits from the current,
    # the class name will be added to plugins
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.plugins.append(cls)

    ## Optional Abstract ##
    # These methods can be reimplemented by the downloader,
    # however that isn't needed as otherwise the methods below
    # will be used instead. 
       
    def checkExists(self, url:str) -> bool:
        """
        Checks if the URL provided is valid

        :param url(str): The url provided

        :return bool: True exists, False doesn't
        """
        return requests.head(url, allow_redirects=True).status_code == 200
    
    def checkDir(self, url:str) -> bool:
        """
        Checks if the URL provided is a direct RGDS file or a directory

        :param url(str): The url provided

        :return bool: True if directory, False if is RGDS
        """
        response = requests.head(url, allow_redirects=True)
        contentType = response.headers['content-type']

        return contentType!='application/octet-stream'

    def readYaml(self, url:str) -> list:
        """
        Reads the YAML file to determine which datasets should be imported.

        :param url(str): The url to the YAML file

        :return list(dict): List of datasets to download and import
        """
        toImportDatasets = []
        resp = requests.get(url, allow_redirects=True)
        if resp.ok:
            c = yaml.safe_load(resp.content.decode("utf-8"))
            print("Got dataset info from YAML for '"+c['title']+"'.")
            for dataset in c['datasets']:
                if dataset['import']==True:
                    toImportDatasets.append(dataset)
        return toImportDatasets

    def download(self, url:str, fname:str, chunk_size:int=1024) -> bool:
        """
        Downloads the file directly from a url to a specified filename

        :param url(str): The url to the direct file (that is going to this url should download)
        :param fname(str): The filename for the file to be saved as
        :param chunk_size(int): Optional, the chunk size to download the file. Default is 1024

        :return bool: if the download was sucessful
        """
        resp = requests.get(url, stream=True)
        if resp.ok:
            total = int(resp.headers.get('content-length', 0))
            with open(fname, 'wb') as file, tqdm.tqdm(
                desc=fname,
                total=total,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in resp.iter_content(chunk_size=chunk_size):
                    size = file.write(data)
                    bar.update(size)
            return True
        return False
    
    ## Required Abstract ##
    # These methods must be implemented by the downloader

    @abstractmethod
    def getYamlUrl(self, url:str) -> str:
        """
        Gets a YAML file's URL

        :param url(str): The url as provided by the user 

        :return str: The YAML url
        """

    @abstractmethod
    def getDownloadUrl(self, url: str, dataset: str) -> str:
        """
        Gets a file (and does whatever processing is needed to get the download URL,
        you may decide to use your own methods if needed.)

        :param url(str): The url as provided by the user 
        :param dataset(str): The dataset path in relation to top level

        :return str: The direct downloadable url
        """


def load_module(path):
    name = os.path.split(path)[-1]
    spec = util.spec_from_file_location(name, path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module  

path = os.path.abspath("downloaders")
for name in os.listdir(path):
    fullPath = path+"/"+name
    for fname in os.listdir(fullPath):
        if not fname.startswith('.') and \
        fname.startswith('__') and fname.endswith('.py'):
            try:
                load_module(os.path.join(fullPath, fname))
            except Exception:
                traceback.print_exc()