from remotefile.remote_file import RemoteFile

import logging
from http.server import HTTPServer

class Server(RemoteFile):
    def __init__(self, path, *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        self.port = kwargs['port'] if 'port' in kwargs else 8000

    def serve_forever(self, *args):
        self.configure_loggings()
        handler = self.load_as_module('handler', force=True)
        Handler = handler.get_handler(*args)
        server = HTTPServer(('0.0.0.0', self.port), Handler)
        logging.info('Serving at port {:d} with handler: {}'.format(self.port, Handler))
        server.serve_forever()

    def configure_loggings(self):
        root = logging.getLogger()
        [root.removeHandler(handler) for handler in root.handlers or []]

        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
