import os
import sys
import json
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

# ===================================================
# STRIX SECURITY: Carregamento Seguro de Variáveis de Ambiente
# ===================================================
def load_env_file():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip())
        except Exception:
            pass

load_env_file()

def get_api_key():
    return os.environ.get('SELECTUSPAY_API_KEY') or 'mp_live_d619e8f6acab3f3b7ea64e636c042943c67accf0cba07556'

PLAN_WHITELIST = {
    'plano19': {'title': 'VIP 30 Dias', 'unit_price': 1990},
    'plano27': {'title': 'VIP 3 Meses', 'unit_price': 2790},
    'plano39': {'title': 'VIP 1 Ano', 'unit_price': 3990}
}

BLOCKED_PATTERNS = (
    '.env', '.git', '.vscode', '.py', '.json', '.md',
    'package.json', 'vercel.json', 'server.py'
)

class SecureHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Strix Security Headers
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
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

    def send_head(self):
        clean_path = self.path.split('?')[0].lower()
        
        # Bloqueio de arquivos sensíveis e tentativas de directory traversal
        for blocked in BLOCKED_PATTERNS:
            if blocked in clean_path:
                self.send_error(403, "Acesso a este recurso foi bloqueado por politicas de seguranca.")
                return None

        # Bloqueio de qualquer arquivo oculto (iniciado por ponto)
        parts = clean_path.strip('/').split('/')
        for part in parts:
            if part.startswith('.'):
                self.send_error(403, "Arquivos de sistema restritos.")
                return None

        return super().send_head()

    def do_POST(self):
        if self.path.startswith('/api/create-payment'):
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Prevenção de DoS por payloads excessivos (limite de 15KB)
            if content_length > 15360:
                self.send_response(413)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Payload muito extenso"}')
                return

            post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            try:
                body = json.loads(post_data)
            except Exception:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "JSON malformado"}')
                return

            plan_id = body.get('planId', 'plano27')
            if plan_id not in PLAN_WHITELIST:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Plano invalido"}')
                return

            plan = PLAN_WHITELIST[plan_id]

            def sanitize(val):
                if not val or not isinstance(val, str):
                    return None
                cleaned = "".join(c for c in val if c.isalnum() or c in "_-.: ")
                return cleaned[:100]

            payload = {
                'customer': {
                    'name': 'Cliente VIP',
                    'email': 'contato.vip@pagamento.com',
                    'document': '39824317800',
                    'phone': '5511999999999'
                },
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
                sanitized_val = sanitize(body.get(utm))
                if sanitized_val:
                    payload[utm] = sanitized_val

            api_key = get_api_key()
            req = urllib.request.Request(
                'https://www.selectuspay.com.br/api/v1/create-payment',
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'HotChatbot-SecureClient/2.0'
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
                err_resp = json.dumps({'error': 'Falha na comunicacao com gateway'}).encode('utf-8')
                self.send_response(502)
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
    httpd = ThreadingHTTPServer(server_address, SecureHTTPRequestHandler)
    print(f"Servidor Seguro Strix rodando em http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)
