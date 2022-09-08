import json
from http.server import BaseHTTPRequestHandler
from urllib import request


class WrapServer(BaseHTTPRequestHandler):

    description = 'HHHHHHHHHHHHHHHHHHHHHHHHHHHHello World!'
    acstatus = None

    def __init__(self, *args, **kwargs):
        acinfo = request.urlopen('http://localhost:8081/INFO').read()
        self.acstatus = json.loads(acinfo.decode("utf8"))
        super().__init__(*args, **kwargs)

    def do_GET(self):
        print("SELFACSTATUS", self.acstatus)

        current_status = self.acstatus
        current_status['description'] = self.description

        self.send_response(200)
        self.send_header('Content-Type',
                         'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(current_status).encode('utf-8'))


if __name__ == '__main__':
    print("Demo mode - Standalone WrapServer")
    from http.server import HTTPServer
    server = HTTPServer(('0.0.0.0', 1980), WrapServer)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
