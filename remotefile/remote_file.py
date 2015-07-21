import os, sys, copy, logging, glob
from urllib.parse import urlparse
from importlib.machinery import SourceFileLoader

class RemoteFile:
    @classmethod
    def build(cls, path, *args, **kwargs):
        url = urlparse(path)

        if cls.is_s3_url(url):
            from remotefile.s3_file import S3File
            return S3File(url, *args, **kwargs)
        elif cls.is_http_url(url):
            from remotefile.http_file import HTTPFile
            return HTTPFile(url, *args, **kwargs)
        else:
            return RemoteFile(url, *args, **kwargs)

    def __init__(self, url, *args, **kwargs):
        self.url = url

        if self.is_local_file():
            self.local_path = self.url.path

    def download(self): return False

    def exists_in_local(self):
        return os.path.isfile(self.local_path)

    def exists(self):
        return os.path.isfile(self.local_path)

    def upload(self, src):
        raise TypeError()

    def upload_with_exception(self, src):
        if not self.upload(src):
            raise Exception('Fail to upload files... src: {}, dest: {}'.format(src.local_path, self.url.geturl()))

    def upload_to(self, destination):
        return destination.upload(self)

    def get_file_path(self, force=False): return self.local_path

    def enable(self, force=False, **kwargs):
        if self.is_local_file():
            return self.exists_in_local()
        elif not force and self.exists_in_local():
            return True
        else:
            return self.download(**kwargs)


    def open(self, **kwargs):
        return open(self.get_file_path(**kwargs), 'rb')

    def read(self, force=False):
        with self.open(force=force) as f: return f.read()

    def load_as_module(self, name, **kwargs):
        if self.enable(**kwargs):
            return SourceFileLoader(name, self.local_path).load_module()
        else:
            return None

    @classmethod
    def is_s3_url(cls, url):
        return url.scheme == 's3'
    def is_s3_file(self):
        return type(self).is_s3_url(self.url)

    @classmethod
    def is_http_url(cls, url):
        return url.scheme == 'http' or url.scheme == 'https'
    def is_http_file(self):
        return type(self).is_http_url(self.url)

    @classmethod
    def is_local_url(cls, url):
        return not cls.is_s3_url(url) and not cls.is_http_url(url)
    def is_local_file(self):
        return type(self).is_local_url(self.url)

    def mkdir_p(self):
        os.makedirs(os.path.dirname(self.local_path), exist_ok=True)

    @staticmethod
    def is_using_cache():
        return os.environ.get('USE_CACHE') == '1'
