from remotefile import HTTPFile, RemoteFile
from expects import *
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest.mock import patch
import os, io, re
import urllib.request as request
from urllib.error import HTTPError

with description(HTTPFile):
    with before.each:
        self.sample_url = 'https://raw.githubusercontent.com/hiroara/remotefile-python/master/README.md'
        self.cache_dir = TemporaryDirectory()
        self.remote_file = RemoteFile(self.sample_url, cache_dir=self.cache_dir.name)

    with after.each:
        self.cache_dir.cleanup()

    with it('should recognized as an local file'):
        expect(self.remote_file.is_s3_file()).to(be_false)
        expect(self.remote_file.is_http_file()).to(be_true)
        expect(self.remote_file.is_local_file()).to(be_false)


    with description('get_local_path method'):
        with it('should return url'):
            under_cache_path = self.remote_file.remote.get_local_path().split(self.cache_dir.name)[1]
            expected_path = os.path.join('/', self.remote_file.url.netloc, re.sub('^/', '', self.remote_file.url.path))
            expect(under_cache_path).to(equal(expected_path))


    with description('exists method'):
        with context('when file exists'):
            with it('should return True'):
                with patch.object(request, 'urlretrieve') as urlretrieve:
                    expect(self.remote_file.exists()).to(be_true)
                    expect(urlretrieve.called).to(be_true)


        with context('when file does not exist'):
            with it('should return False'):
                err = HTTPError(self.sample_url, 404, 'file not found', {}, NamedTemporaryFile())
                with patch.object(request, 'urlretrieve', side_effect=err) as urlretrieve:
                    expect(self.remote_file.exists()).to(be_false)
                    expect(urlretrieve.called).to(be_true)
