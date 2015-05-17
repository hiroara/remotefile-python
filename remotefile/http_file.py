from remotefile.remote_file import RemoteFile

import logging, os, re
import urllib.request as request
from urllib.error import HTTPError

class HTTPFile(RemoteFile):
    def __init__(self, url, cache_dir='/tmp/http', region_name=None):
        self.url = url
        self.cache_dir = cache_dir
        self.local_path = self.get_local_path()
        self.downloaded = False

    def get_local_path(self):
        return os.path.join(self.cache_dir, self.url.netloc, re.sub('^/', '', self.url.path))

    def exists(self):
        return self.download()

    def download(self):
        if self.downloaded: return True
        self.mkdir_p()
        try:
            request.urlretrieve(self.url.geturl(), self.local_path, lambda blocknum, blocksize, totalsize: logging.info('Downloading {} ({:d}/{:d})'.format(self.local_path, blocknum * blocksize, totalsize)))
            logging.info('Downloading {} has been completed.'.format(self.local_path))
            self.downloaded = True
            return True
        except HTTPError as err:
            logging.info('Returns error via HTTP on downloading {}. {}'.format(self.url.geturl(), err))
            return False
