from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import requests.adapters
import threading
import requests
import blocker
import config
import socket

session = requests.Session()
session.verify = False

adapter = requests.adapters.HTTPAdapter(
    pool_connections=100,
    pool_maxsize=100,
    max_retries = 2,
    pool_block = False
)

session.mount("http://", adapter)
session.mount("https://", adapter)

class MITMProxyServer(BaseHTTPRequestHandler):
    # Function for logging
    def log(self, value: str | None, category: str | None) -> None:
        if not config.LOG:
            return
    
        if category:
            num_chars = 50 - (len(category)//2)
            print("="*num_chars + f"{category}" + "="*num_chars)
        
        if value:
            print(value)

    # Handling special urls
    def get_url(self) -> None:
        if self.path.startswith("http") or self.path.startswith("https"):
            BLOCKER = blocker.Blocker(self.path)
            self.url: str = BLOCKER.check_url()
        else: 
            tempUrl = "https://" + self.path
            BLOCKER = blocker.Blocker(tempUrl)
            self.url: str = BLOCKER.check_url()
    
    def do_GET(self): self.handle_request() # GET requests
    def do_POST(self): self.handle_request() # POST requests
    def do_PUT(self): self.handle_request() # PUT requests
    def do_DELETE(self): self.handle_request() # DELETE requests
    def do_HEAD(self): self.handle_request() # HEAD requests
    def do_OPTIONS(self): self.handle_request() # OPTIONS requests
    
    # HTTPS handling
    def do_CONNECT(self) -> None : 
        self.get_url()
        try:
            host, port = self.url.strip("http://").strip("https://").split(":")
            port = int(port)
        except Exception:
            host = None 
            port = None
        
        self.log(f"CONNECT {host} : {port}", "[COMMAND + URL]")

        try : 
            # Connecting to the site ( Host and Port )
            target_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((host, port))

            self.log(None, "[REQUEST HEADERS]")
            for key, value in self.headers.items(): self.log(f"{key} : {value}", None)
            
            # Sending Success
            self.send_response(200, "Connection Established")
            self.end_headers()
            
            client_socket = self.request
            
            # Forwarding the data
            def forward(source, dest):
                try:
                    while True:
                        data: bytes = source.recv(8192)
                        if not data:
                            break
                        dest.send(data)
                except:
                    pass
                finally:
                    # Close both sockets if either direction fails
                    client_socket.close()
                    target_socket.close()

            # Create threads for concurrnecy
            client_to_target = threading.Thread(target=forward, args=(client_socket, target_socket), daemon=True)
            target_to_client = threading.Thread(target=forward, args=(target_socket, client_socket), daemon=True)
            
            client_to_target.start()
            target_to_client.start()
            
            client_to_target.join()
            target_to_client.join()

        except Exception as e:
            print(f"Tunnel Error: {e}")
            try:
                self.send_error(502, f"Bad Gateway: {str(e)}")
            except:
                pass

    # Creating custom arguments for the requests library
    def handle_requests_arguments(self) -> dict: 
        content_length: str | None = self.headers.get("Content-Length")
        self.body = None
        
        if content_length and self.command in ['POST', 'PUT', 'PATCH']:
            self.body = self.rfile.read(int(content_length))
            self.log(self.body.decode(), "[REQUEST CONTENT]")

        self.log(None, "[REQUEST HEADERS]")

        headers: dict[str, str] = {}
        for header, value in self.headers.items():
            if header.lower() not in config.DISALLOWED_HEADERS:
                self.log(f"{header} : {value}", None)
                headers[header] = value

        request_arguments: dict = {
            'method': self.command,
            'url': self.url,
            'headers': headers,
            'data': self.body,
            'allow_redirects': False,  # Don't automatically follow redirects
            'verify': False,  # Disable SSL verification (for HTTPS)
            'stream': True
        }

        return request_arguments
    
    # Handling HTTP requests
    def handle_request(self) -> None:
        try:
            self.get_url()
            self.log(f"{self.command} {self.url}", "[COMMAND + URL]")

            # Sending a request to the site
            request_args: dict = self.handle_requests_arguments()
            response: requests.Response = session.request(**request_args)
            
            bytes_in = len(self.body) if self.body else 0
            bytes_out = len(response.content)
            
            self.log(None, "[RESPONSE HEADERS]")
            for key, value in response.headers.items(): self.log(f"{key} : {value}", None)

            self.log(str(response.status_code) + f"\n\n[ -> ] BYTES IN : {bytes_in}" + f"\n[ <- ] BYTES OUT : {bytes_out}", 
                     "[RESPONSE STATUS CODE + BYTES IN / OUT]")
            
            self.log(str(response.content.decode()[:500]), "[RESPONSE BODY]")
             
            self.send_response(response.status_code)

            for header, value in response.headers.items():
                if header.lower() not in config.DISALLOWED_HEADERS:
                    self.send_header(header, value)

            self.end_headers()

            self.wfile.write(response.content)

        except requests.exceptions.Timeout:
            print("\n[ERROR] Request timeout")
            self.send_error(504, "Gateway Timeout")
        except requests.exceptions.ConnectionError as e:
            print(f"\n[ERROR] CONNECTION ERROR: {e}")
            self.send_error(502, "Bad Gateway")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {str(e)}")
            self.send_error(500, "Internal Server Error")

class ThreadingServer(ThreadingMixIn, HTTPServer):
    daemon_threads: bool = True
    allow_reuse_address: bool = True
