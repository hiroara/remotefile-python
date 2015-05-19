from urllib.parse import urlparse
import os, sys, copy, logging, glob

class RemoteFile:
    def __init__(self, path, *args, **kwargs):
        self.url = urlparse(path)

        if self.is_s3_file():
            from remotefile.s3_file import S3File
            self.remote = S3File(self.url, *args, **kwargs)
        elif self.is_http_file():
            from remotefile.http_file import HTTPFile
            self.remote = HTTPFile(self.url, *args, **kwargs)
        else:
            self.remote = None

        if self.is_local_file():
            self.local_path = self.url.path
        else:
            self.local_path = self.remote.local_path

    def download(self):
        if self.remote == None: return False
        logging.info('Start to download {}.'.format(self.local_path))
        return self.remote.download()

    def exists_in_local(self):
        return os.path.isfile(self.local_path)

    def exists(self):
        if self.is_local_file():
            return os.path.isfile(self.local_path)
        else:
            return self.remote.exists()

    def upload(self, src):
        if self.is_local_file(): raise TypeError()
        if not isinstance(src, RemoteFile): raise TypeError()

        files = glob.glob(src.get_file_path())
        if len(files) > 1:
            return all([self.remote.upload(RemoteFile(f), True) for f in files])
        elif len(files) == 1:
            return self.remote.upload(RemoteFile(files[0]), False)

        return False

    def upload_with_exception(self, src):
        if not self.upload(src):
            raise Exception('Fail to upload files... src: {}, dest: {}'.format(src.local_path, self.url.geturl()))

    def upload_to(self, destination):
        return destination.upload(self)

    def get_file_path(self, force=False):
        if self.remote == None: return self.local_path
        if not force and os.path.isfile(self.local_path): return self.local_path

        if not self.download():
            logging.info('Remote file not found: {}'.format(self.remote.url))
        return self.remote.local_path

    def enable(self, **kwargs):
        if self.exists():
            self.get_file_path(**kwargs)
            return True
        else:
            return False

    def open(self, **kwargs):
        return open(self.get_file_path(**kwargs), 'rb')

    def read(self, force=False):
        with self.open(force=force) as f: return f.read()

    def is_s3_file(self):
        return self.url.scheme == 's3'

    def is_http_file(self):
        return self.url.scheme == 'http' or self.url.scheme == 'https'

    def is_local_file(self):
        return not self.is_s3_file() and not self.is_http_file()

    def mkdir_p(self):
        os.makedirs(os.path.dirname(self.local_path), exist_ok=True)
