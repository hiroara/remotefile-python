from remotefile import Server, RemoteFile
from expects import *
from tempfile import NamedTemporaryFile
from unittest.mock import patch
import os
from http.server import HTTPServer

def write_script(filepath, content):
    with open(filepath, 'w') as f: f.write(content)

with description(Server):
    with describe('exec_script method'):
        with before.each:
            self.server_script_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'sample_server.py')
            self.server = Server(self.server_script_path)

        with it('should enable script file forcibly'):
            with patch.object(Server, 'enable'):
                with patch.object(HTTPServer, 'serve_forever') as serve_method:
                    self.server.serve_forever()
                    expected_args = ((), { 'force': True })
                    expect(self.server.enable.call_args).to(equal(expected_args))
                    expect(serve_method.called).to(be_true)
