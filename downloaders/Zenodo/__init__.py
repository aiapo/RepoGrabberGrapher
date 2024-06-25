from app.core.downloader import Downloader
from urllib.parse import urlparse


# This is a Zenodo downloader
class Zenodo(Downloader):
    NAME = "Zenodo"
    BASEDOMAINS = ("zenodo.org", "www.zenodo.org", "sandbox.zenodo.org")

    def getYamlUrl(self, url):
        return getZenodoAPI(url) + "/dataset.yaml/content"

    def getDownloadUrl(self, url, dataset):
        return getZenodoAPI(url) + dataset + "/content"


def getZenodoAPI(url):
    path = urlparse(url).path.split("/")
    return "https://" + urlparse(url).netloc + "/api/records/" + path[2] + "/files/"
