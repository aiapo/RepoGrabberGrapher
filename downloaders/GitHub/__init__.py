from app.core.downloader import Downloader
from urllib.parse import urlparse
import re

# This is a GitHub downloader
class GitHub(Downloader):
    NAME = 'GitHub'
    BASEDOMAINS = ('github.com','www.github.com')

    def getDownloadUrl(self,url):
        repo = re.sub('/blob', '', urlparse(url).path)
        if repo.endswith(".rgds"):
            return "https://raw.githubusercontent.com"+repo
        else:
            return ""