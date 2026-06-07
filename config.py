LOG: bool = True

HOST: str = "127.0.0.1"
PORT: int = 8080

DISALLOWED_HEADERS = ['connection', 'keep-alive', 'proxy-connection', 'transfer-encoding', 'upgrade', 'proxy-authorization']

UPSTREAM_PROXY_HTTP: str = "http://127.0.0.1:8085"
UPSTREAM_PROXY_HTTPS: str = "http://127.0.0.1:8085"

BLOCKED_SITES = ["chat.deepseek.com"] # FOR EXAMPLE
