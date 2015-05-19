from remotefile import RemoteFile
from expects import *
from urllib.parse import ParseResult
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest.mock import MagicMock
import os, io


with description(RemoteFile):
    with context('when provide a local path'):
        with before.each:
            self.temp_file = NamedTemporaryFile()
            self.path = self.temp_file.name
            self.remote_file = RemoteFile(self.path)

        with after.each:
            self.temp_file.close()

        with it('should recognized as an local file'):
            expect(self.remote_file.is_s3_file()).to(be_false)
            expect(self.remote_file.is_http_file()).to(be_false)
            expect(self.remote_file.is_local_file()).to(be_true)

        with it('should have url'):
            expect(self.remote_file.url).to(be_a(ParseResult))
            expect(self.remote_file.url.geturl()).to(equal(self.path))


        with description('download method'):
            with it('should return False'):
                expect(self.remote_file.download()).to(be_false)


        with description('exists method'):
            with context('when file exists'):
                with it('should return True'):
                    expect(self.remote_file.exists()).to(be_true)

            with context('when file does not exist'):
                with before.each:
                    self.temp_file.close() # delete

                with it('should return False'):
                    expect(self.remote_file.exists()).to(be_false)


        with description('upload method'):
            with it('should raise TypeError'):
                expect(lambda: self.remote_file.upload()).to(raise_error(TypeError))


        with description('upload_to method'):
            with before.each:
                self.other_temp_file = NamedTemporaryFile()
                self.other_file = RemoteFile(self.other_temp_file.name)
                self.other_file.upload = MagicMock()
            with after.each:
                self.other_temp_file.close()

            with it('should call upload method of destination'):
                self.remote_file.upload_to(self.other_file)
                expected_args = ((self.remote_file,),)
                expect(self.other_file.upload.call_args).to(equal(expected_args))


        with description('get_file_path method'):
            with it('should return local_file attribute'):
                expect(self.remote_file.get_file_path()).to(equal(self.remote_file.local_path))


        with description('enable method'):
            with it('should not do anything'):
                expect(self.remote_file.enable()).to(be_true)


        with description('open method'):
            with it('should return readable IO object'):
                file_io = self.remote_file.open()
                file_io.close()
                expect(file_io).to(be_a(io.BufferedReader))
                expect(file_io.name).to(equal(self.temp_file.name))


        with description('read method'):
            with before.each:
                self.sample_text = 'This is Sample Text.'
                with open(self.temp_file.name, 'w') as f:
                    f.write(self.sample_text)

            with it('should return content of the file'):
                content = self.remote_file.read().decode('utf-8')
                expect(content).to(equal(self.sample_text))


        with description('mekir_p method'):
            with before.each:
                self.temp_dir = TemporaryDirectory()
                self.temp_dir.cleanup()
                self.remote_file = RemoteFile(os.path.join(self.temp_dir.name, 'test.txt'))

            with after.each:
                self.temp_dir.cleanup()

            with it('should create directory'):
                expect(os.path.isdir(self.temp_dir.name)).to(be_false)
                self.remote_file.mkdir_p()
                expect(os.path.isdir(self.temp_dir.name)).to(be_true)
