from app.core.downloader import Downloader

# This is a generic downloader, assumes that the download url is the given url
class GENERIC(Downloader):
    NAME = 'Generic'
    def getDownloadUrl(self,url):
        return url