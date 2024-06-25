from app.core.downloader import Downloader
from urllib.parse import urlparse


# This is a GitHub downloader
class GitHub(Downloader):
    NAME = "GitHub"
    BASEDOMAINS = ("github.com", "www.github.com")

    def getYamlUrl(self, url):
        return getGitHubRaw(url) + "/dataset.yaml"

    def getDownloadUrl(self, url, dataset):
        return getGitHubRaw(url) + dataset


def getGitHubRaw(url):
    path = urlparse(url).path
    print(path.split("/"))
    if len(path.split("/")) == 3:
        return "https://raw.githubusercontent.com" + path + "/main/"
    elif len(path.split("/")) == 4:
        return "https://raw.githubusercontent.com" + path
    else:
        return None
