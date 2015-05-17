from remotefile.remote_file import RemoteFile

import logging
from socketserver import TCPServer

class Server(RemoteFile):
    def __init__(self, path, *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        self.port = kwargs['port'] if 'port' in kwargs else 8000

    def serve_forever(self, *args):
        self.enable(force=True)
        from importlib.machinery import SourceFileLoader
        handler = SourceFileLoader('handler', self.local_path).load_module()
        Handler = handler.get_handler(*args)
        server = TCPServer(('0.0.0.0', self.port), Handler)
        logging.info('Serving at port {:d} with handler: {}'.format(self.port, Handler))
        server.serve_forever()
