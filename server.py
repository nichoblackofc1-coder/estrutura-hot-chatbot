import os
import sys
import json
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

API_KEY = 'mp_live_d619e8f6acab3f3b7ea64e636c042943c67accf0cba07556'

PLAN_CONFIG = {
    'plano19': {'title': 'VIP 30 Dias', 'unit_price': 1990},
    'plano27': {'title': 'VIP 3 Meses', 'unit_price': 2790},
    'plano39': {'title': 'VIP 1 Ano', 'unit_price': 3990}
}

class FastHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        
        path = self.translate_path(self.path)
        if path.endswith(('.jpg', '.jpeg', '.png', '.webp', '.svg', '.mp4', '.woff2', '.ttf', '.ico')):
            self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
        elif path.endswith('.html') or self.path == '/' or self.path.startswith('/?'):
            self.send_header('Cache-Control', 'no-cache, must-revalidate')
            
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path.startswith('/api/create-payment'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            try:
                body = json.loads(post_data)
            except Exception:
                body = {}

            plan_id = body.get('planId', 'plano27')
            plan = PLAN_CONFIG.get(plan_id, PLAN_CONFIG['plano27'])

            payload = {
                'customer': body.get('customer', {
                    'name': 'Assinante VIP',
                    'email': 'assinante@vipclub.com',
                    'document': '39824317800',
                    'phone': '5511999999999'
                }),
                'payment_method': 'pix',
                'items': [
                    {
                        'title': plan['title'],
                        'unit_price': plan['unit_price'],
                        'quantity': 1
                    }
                ]
            }

            for utm in ['utm_source', 'utm_campaign', 'utm_medium', 'utm_content', 'utm_term']:
                if body.get(utm):
                    payload[utm] = body[utm]

            req = urllib.request.Request(
                'https://www.selectuspay.com.br/api/v1/create-payment',
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {API_KEY}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0'
                }
            )

            try:
                with urllib.request.urlopen(req, timeout=10) as res:
                    res_body = res.read()
                    self.send_response(res.status)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(res_body)
            except urllib.error.HTTPError as e:
                err_body = e.read()
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(err_body)
            except Exception as e:
                err_resp = json.dumps({'error': str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(err_resp)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run(port=8000):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, FastHTTPRequestHandler)
    print(f"Servidor ultra rapido rodando em http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)
