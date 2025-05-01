# caching_proxy_select.py
import socket
import select
import threading
from urllib.parse import urlparse
from collections import OrderedDict
import sys

class CachingProxy:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.cache = OrderedDict()
        self.cache_size = 100  # Максимальное количество кэшируемых элементов
        self.lock = threading.Lock()
        self.running = False

    def start(self):
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"Прокси-сервер запущен на {self.host}:{self.port}")
        
        sockets = [server_socket]
        
        try:
            while self.running:
                readable, _, _ = select.select(sockets, [], [], 1)
                
                for sock in readable:
                    if sock == server_socket:
                        client_socket, addr = server_socket.accept()
                        sockets.append(client_socket)
                        print(f"Новое соединение от {addr}")
                    else:
                        try:
                            data = sock.recv(4096)
                            if data:
                                self.handle_request(sock, data)
                            else:
                                sock.close()
                                sockets.remove(sock)
                        except:
                            sock.close()
                            sockets.remove(sock)
        except KeyboardInterrupt:
            print("Остановка прокси-сервера...")
        finally:
            server_socket.close()
            self.running = False

    def handle_request(self, client_socket, data):
        try:
            request = data.decode('utf-8')
            lines = request.split('\n')
            if not lines:
                return
                
            method, url, _ = lines[0].split()
            
            if method != 'GET':
                client_socket.send(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
                return
                
            parsed_url = urlparse(url)
            host = parsed_url.netloc
            path = parsed_url.path
            
            cache_key = f"{host}{path}"
            
            # Проверяем кэш
            with self.lock:
                if cache_key in self.cache:
                    print(f"Возвращаем ответ из кэша для {cache_key}")
                    client_socket.sendall(self.cache[cache_key])
                    return
                    
            # Если нет в кэше, делаем запрос к целевому серверу
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((host, 80))
            
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            target_socket.send(request.encode())
            
            response = b''
            while True:
                data = target_socket.recv(4096)
                if not data:
                    break
                response += data
            
            # Кэшируем ответ
            with self.lock:
                self.cache[cache_key] = response
                if len(self.cache) > self.cache_size:
                    self.cache.popitem(last=False)
            
            client_socket.sendall(response)
            target_socket.close()
            
        except Exception as e:
            print(f"Ошибка обработки запроса: {e}")
            client_socket.send(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8080
        
    proxy = CachingProxy(port=port)
    proxy.start()