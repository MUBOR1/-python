# caching_proxy_threadpool.py
import socket
import threading
from urllib.parse import urlparse
from collections import OrderedDict
import queue
import sys

class ThreadPoolCachingProxy:
    def __init__(self, host='0.0.0.0', port=8080, pool_size=10):
        self.host = host
        self.port = port
        self.pool_size = pool_size
        self.cache = OrderedDict()
        self.cache_size = 100
        self.cache_lock = threading.Lock()
        self.task_queue = queue.Queue()
        self.worker_threads = []
        self.running = False

    def start(self):
        self.running = True
        
        # Создаем рабочие потоки
        for _ in range(self.pool_size):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()
            self.worker_threads.append(thread)
            
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)
        
        print(f"Прокси с пулом потоков ({self.pool_size}) запущен на {self.host}:{self.port}")
        
        try:
            while self.running:
                client_socket, addr = server_socket.accept()
                print(f"Принято соединение от {addr}")
                self.task_queue.put(client_socket)
                
        except KeyboardInterrupt:
            print("Остановка прокси-сервера...")
        finally:
            self.running = False
            server_socket.close()
            
            # Ожидаем завершения всех задач
            self.task_queue.join()
            
            # Останавливаем рабочие потоки
            for _ in range(self.pool_size):
                self.task_queue.put(None)
                
            for thread in self.worker_threads:
                thread.join()

    def worker(self):
        while self.running:
            client_socket = self.task_queue.get()
            
            if client_socket is None:
                break
                
            try:
                self.handle_client(client_socket)
            except Exception as e:
                print(f"Ошибка в рабочем потоке: {e}")
            finally:
                self.task_queue.task_done()

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
    if len(sys.argv) > 2:
        port = int(sys.argv[1])
        pool_size = int(sys.argv[2])
    elif len(sys.argv) > 1:
        port = int(sys.argv[1])
        pool_size = 10
    else:
        port = 8080
        pool_size = 10
        
    proxy = ThreadPoolCachingProxy(port=port, pool_size=pool_size)
    proxy.start()