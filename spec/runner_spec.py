from remotefile import Runner, RemoteFile
from expects import *
from tempfile import NamedTemporaryFile
from unittest.mock import patch

def write_script(filepath, content):
    with open(filepath, 'w') as f: f.write(content)

with description(Runner):
    with describe('exec_script method'):
        with before.each:
            self.temp_script = NamedTemporaryFile()

        with it('should enable script file forcibly'):
            self.runner = Runner(self.temp_script.name)
            with patch.object(RemoteFile, 'enable') as method:
                self.runner.exec_script()
                expected_args = ((), { 'force': True })
                expect(self.runner.remote.enable.call_args).to(equal(expected_args))

        with context('a script file has content'):
            with before.each:
                self.sample_text = 'Write on script!'
                self.test_arg = 'Test Argument with Whitespace'
                write_script(self.temp_script.name, '''
import sys, os
script_path = sys.argv[1]
with open(script_path, 'w') as f:
    f.write('{}\\n')
    f.write(sys.argv[2] + '\\n')
    f.write('true' if os.environ.get('USE_CACHE') == '1' else 'false')
                '''.format(self.sample_text))
                self.result_file = NamedTemporaryFile()

            with after.each:
                self.result_file.close()

            with it('should execute provided script'):
                self.runner = Runner(self.temp_script.name)
                self.runner.exec_script(self.result_file.name, self.test_arg)
                f = None
                try:
                    f = RemoteFile.build(self.result_file.name).open()
                    lines = f.readlines()
                    expect(lines[0].rstrip().decode('utf-8')).to(equal(self.sample_text))
                    expect(lines[1].rstrip().decode('utf-8')).to(equal(self.test_arg))
                    expect(lines[2].rstrip().decode('utf-8')).to(equal('false'))
                finally:
                    if f is not None: f.close()

            with it('should execute provided script'):
                self.runner = Runner(self.temp_script.name, use_cache=True)
                self.runner.exec_script(self.result_file.name, self.test_arg)
                f = None
                try:
                    f = RemoteFile.build(self.result_file.name).open()
                    lines = f.readlines()
                    expect(lines[2].rstrip().decode('utf-8')).to(equal('true'))
                finally:
                    if f is not None: f.close()
