import http.server
import re
import traceback

from . import register_command
from .pretty import print_info, print_fail
from ..request import Request


class APIProxyHandler(http.server.BaseHTTPRequestHandler):

    def do_proxy(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)
        path = re.sub(r'^/?v(\d+)/', '/', self.path)
        rqst = Request(self.command, path, body)
        resp = rqst.send()
        self.send_response(resp.status, resp.reason)
        self.send_header('Content-Type', resp.content_type)
        self.send_header('Content-Length', resp.content_length)
        self.end_headers()
        self.wfile.write(resp.content)

    def do_HEAD(self):
        self.do_proxy()

    def do_GET(self):
        self.do_proxy()

    def do_POST(self):
        self.do_proxy()

    def do_PUT(self):
        self.do_proxy()

    def do_DELETE(self):
        self.do_proxy()

    def do_PATCH(self):
        self.do_proxy()

    def do_OPTIONS(self):
        self.do_proxy()


@register_command
def proxy(args):
    '''
    Run a non-encyprted non-authorized API proxy server.
    Use this only for development and testing!
    '''
    print_info('Starting an insecure API proxy at http://{0}:{1}'
               .format(args.bind, args.port))
    try:
        addr = (args.bind, args.port)
        httpd = http.server.HTTPServer(addr, APIProxyHandler)
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print()
        print_info('Terminated.')
    except:
        print_fail('Unexpected error!')
        traceback.print_exc()


proxy.add_argument('--bind', type=str, default='localhost',
                   help='The IP/host address to bind this proxy.')
proxy.add_argument('-p', '--port', type=int, default=8084,
                   help='The TCP port to accept non-encrypted non-authorized '
                        'API requests. (default: 8084)')
