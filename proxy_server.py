import socket
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer

class ProxyHandler(BaseHTTPRequestHandler):
    def do_CONNECT(self):
        # For HTTPS requests, establish a tunnel to the server
        host, port = self.path.split(":")
        port = int(port)

        try:
            with socket.create_connection((host, port)) as sock:
                self.send_response(200)
                self.end_headers()
                
                self.connection.setblocking(False)
                sock.setblocking(False)
                
                # Tunnel data between the client and the server
                while True:
                    data_from_client = self.connection.recv(4096)
                    if data_from_client:
                        sock.sendall(data_from_client)
                    
                    data_from_server = sock.recv(4096)
                    if data_from_server:
                        self.connection.sendall(data_from_server)
                    
                    if not data_from_client and not data_from_server:
                        break
        except Exception as e:
            print(f"Error handling CONNECT: {e}")
            self.send_error(502, "Bad Gateway")

    def do_GET(self):
        self.forward_request()

    def do_POST(self):
        self.forward_request()

    def forward_request(self):
        # Extract request details
        url = self.path
        host = self.headers['Host']
        method = self.command

        # Forward the request to the actual server
        try:
            conn = http.client.HTTPSConnection(host) if self.path.startswith("https") else http.client.HTTPConnection(host)
            
            # Forward headers and body to the destination server
            headers = {key: value for key, value in self.headers.items()}
            content_length = int(headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            conn.request(method, url, body=body, headers=headers)
            response = conn.getresponse()

            # Relay the response status and headers
            self.send_response(response.status, response.reason)
            for key, value in response.getheaders():
                self.send_header(key, value)
            self.end_headers()

            # Relay the response content
            response_data = response.read()
            self.wfile.write(response_data)

            conn.close()
        except Exception as e:
            print(f"Error forwarding request: {e}")
            self.send_error(502, "Bad Gateway")

def run_server(server_class=HTTPServer, handler_class=ProxyHandler, port=8002):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting proxy server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
