from remotefile import S3File, RemoteFile
from expects import *
from tempfile import TemporaryDirectory, NamedTemporaryFile
from unittest.mock import patch, MagicMock
import os, re

from boto.s3.bucket import Bucket
from boto.s3.key import Key

with description(S3File):
    with before.each:
        self.sample_url = 's3://ari-hiro.com/example/remotefile-python/test.txt'
        self.cache_dir = TemporaryDirectory()
        self.region = 'ap-northeast-1'
        self.remote_file = RemoteFile(self.sample_url, cache_dir=self.cache_dir.name, region_name=self.region)

        self.bucket = Bucket()
        self.bucket.get_key = MagicMock('get_key')
        self.mocked_obj = Key(self.remote_file.url.netloc, self.remote_file.url.path)


    with after.each:
        self.cache_dir.cleanup()

    with it('should recognized as an local file'):
        expect(self.remote_file.is_s3_file()).to(be_true)
        expect(self.remote_file.is_http_file()).to(be_false)
        expect(self.remote_file.is_local_file()).to(be_false)


    with description('get_local_path method'):
        with it('should return url'):
            under_cache_path = self.remote_file.remote.get_local_path().split(self.cache_dir.name)[1]
            expected_path = os.path.join('/', self.region, self.remote_file.url.netloc, re.sub('^/', '', self.remote_file.url.path))
            expect(under_cache_path).to(equal(expected_path))


    with description('exists method'):
        with context('when file exists'):
            with before.each:
                self.bucket.get_key.return_value = self.mocked_obj

            with it('should return True'):
                with patch.object(S3File, '_S3File__get_s3_bucket', return_value=self.bucket):
                    expect(self.remote_file.exists()).to(be_true)


        with context('when file does not exist'):
            with before.each:
                self.bucket.get_key.return_value = None

            with it('should return False'):
                with patch.object(S3File, '_S3File__get_s3_bucket', return_value=self.bucket):
                    expect(self.remote_file.exists()).to(be_false)


    with description('download method'):
        with context('when file exists'):
            with before.each:
                self.bucket.get_key.return_value = self.mocked_obj

            with it('should download to local and return True'):
                with patch.object(S3File, '_S3File__get_s3_bucket', return_value=self.bucket):
                    with patch.object(self.mocked_obj, 'get_contents_to_file') as getter:
                        expect(self.remote_file.download()).to(be_true)
                        expect(getter.called).to(be_true)
                        first_arg = getter.call_args[0][0].name
                        expect(first_arg).to(equal(self.remote_file.get_file_path()))


        with context('when file does not exist'):
            with before.each:
                self.bucket.get_key.return_value = None

            with it('should return False'):
                with patch.object(S3File, '_S3File__get_s3_bucket', return_value=self.bucket):
                    with patch.object(self.mocked_obj, 'get_contents_to_file') as getter:
                        expect(self.remote_file.download()).to(be_false)
                        expect(getter.called).to(be_false)


    with description('upload method'):
        with before.each:
            self.src_temp_file = NamedTemporaryFile()
            with open(self.src_temp_file.name, 'w') as f: f.write('Some content')
            self.src_file = RemoteFile(self.src_temp_file.name)

        with it('should upload to provided url'):
            with patch.object(S3File, '_S3File__get_s3_bucket', return_value=self.bucket):
                with patch.object(Key, 'set_contents_from_filename') as setter:
                    self.remote_file.upload(self.src_file)
                    expect(setter.called).to(be_true)
                    first_arg = setter.call_args[0][0]
                    expect(first_arg).to(equal(self.src_file.get_file_path()))
