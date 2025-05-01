# caching_proxy_threaded.py
import socket
import threading
from urllib.parse import urlparse
from collections import OrderedDict
import sys

class ThreadedCachingProxy:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.cache = OrderedDict()
        self.cache_size = 100
        self.cache_lock = threading.Lock()
        self.running = False

    def start(self):
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)
        
        print(f"Многопоточный прокси-сервер запущен на {self.host}:{self.port}")
        
        try:
            while self.running:
                client_socket, addr = server_socket.accept()
                print(f"Новое соединение от {addr}")
                
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                thread.daemon = True
                thread.start()
                
        except KeyboardInterrupt:
            print("Остановка прокси-сервера...")
        finally:
            server_socket.close()
            self.running = False

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(4096)
            if not data:
                return
                
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
            
            # Проверка кэша
            with self.cache_lock:
                if cache_key in self.cache:
                    print(f"Возвращаем ответ из кэша для {cache_key}")
                    client_socket.sendall(self.cache[cache_key])
                    return
                    
            # Запрос к целевому серверу
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
            
            # Кэширование ответа
            with self.cache_lock:
                self.cache[cache_key] = response
                if len(self.cache) > self.cache_size:
                    self.cache.popitem(last=False)
            
            client_socket.sendall(response)
            target_socket.close()
            
        except Exception as e:
            print(f"Ошибка обработки запроса: {e}")
            client_socket.send(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
        finally:
            client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8080
        
    proxy = ThreadedCachingProxy(port=port)
    proxy.start()