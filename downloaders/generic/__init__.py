from app.core.downloader import Downloader


# This is a generic downloader, assumes that the download url is the given url
class GENERIC(Downloader):
    NAME = "Generic"

    def getYamlUrl(self, url):
        return url + "/dataset.yaml"

    def getDownloadUrl(self, url, dataset):
        return url + dataset
