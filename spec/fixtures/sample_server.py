from http.server import SimpleHTTPRequestHandler

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        self.send_response(405)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(bytes('Method Not Allowed', 'utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes('<html><head><title>Title goes here.</title></head>', 'utf-8'))
        self.wfile.write(bytes('<body><p>This is a test.</p>', 'utf-8'))
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        self.wfile.write(bytes('<p>You accessed path: %s</p>' % self.path, 'utf-8'))
        self.wfile.write(bytes('</body></html>', 'utf-8'))

def get_handler(): return Handler
