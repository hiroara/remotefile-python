from remotefile import Runner, RemoteFile
from expects import *
from urllib.parse import ParseResult
from tempfile import NamedTemporaryFile
from unittest.mock import patch
import os, io

def write_script(filepath, content):
    with open(filepath, 'w') as f: f.write(content)

with description(Runner):
    with describe('exec_script method'):
        with before.each:
            self.temp_script = NamedTemporaryFile()
            self.runner = Runner(self.temp_script.name)

        with it('should enable script file forcibly'):
            with patch.object(Runner, 'enable') as method:
                self.runner.exec_script()
                expected_args = ((), { 'force': True })
                expect(self.runner.enable.call_args).to(equal(expected_args))

        with context('a script file has content'):
            with before.each:
                self.sample_text = 'Write on script!'
                write_script(self.temp_script.name, '''
import sys
script_path = sys.argv[1]
with open(script_path, 'w') as f:
    f.write('{}\\n')
    f.write(sys.argv[2])
                '''.format(self.sample_text))
                self.result_file = NamedTemporaryFile()

            with after.each:
                self.result_file.close()

            with it('should execute provided script'):
                test_arg = 'Test Argument with Whitespace'
                self.runner.exec_script(self.result_file.name, test_arg)
                try:
                    f = RemoteFile(self.result_file.name).open()
                    lines = f.readlines()
                    expect(lines[0].rstrip().decode('utf-8')).to(equal(self.sample_text))
                    expect(lines[1].rstrip().decode('utf-8')).to(equal(test_arg))
                finally:
                    f.close()
