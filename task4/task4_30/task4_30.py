# http_client_threaded.py
import sys
import socket
import threading
import urllib.parse

class HTTPClientThreaded:
    def __init__(self):
        self.screen_lines = 0
        self.paused = False
        self.lock = threading.Lock()
        self.data_ready = threading.Event()
        self.user_input_ready = threading.Event()
        self.buffer = []
        
    def fetch_url(self, url):
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc
        path = parsed.path if parsed.path else '/'
        
        if not host:
            print("Неверный URL: отсутствует хост")
            return
            
        # Поток для чтения данных
        def network_thread():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, 80))
                
                request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                s.send(request.encode())
                
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                        
                    with self.lock:
                        self.buffer.append(data.decode('utf-8', errors='ignore'))
                        self.data_ready.set()
                        
            except Exception as e:
                print(f"Ошибка сети: {e}")
            finally:
                s.close()
                with self.lock:
                    self.buffer.append(None)  # Маркер конца данных
                    self.data_ready.set()
        
        # Поток для вывода данных
        def display_thread():
            while True:
                self.data_ready.wait()
                
                with self.lock:
                    if not self.buffer:
                        self.data_ready.clear()
                        continue
                        
                    chunk = self.buffer.pop(0)
                    if chunk is None:  # Конец данных
                        break
                        
                    self.display_data(chunk)
                    
                self.data_ready.clear()
        
        # Запускаем потоки
        net_thread = threading.Thread(target=network_thread)
        disp_thread = threading.Thread(target=display_thread)
        
        net_thread.start()
        disp_thread.start()
        
        net_thread.join()
        disp_thread.join()
        
    def display_data(self, text):
        for char in text:
            if self.screen_lines >= 25 and not self.paused:
                print("\nPress space to scroll down...")
                self.paused = True
                
            if self.paused:
                self.user_input_ready.wait()
                self.user_input_ready.clear()
                continue
                
            print(char, end='', flush=True)
            if char == '\n':
                self.screen_lines += 1
                
    def user_input(self):
        while True:
            key = input()
            if key == ' ':
                self.screen_lines = 0
                self.paused = False
                self.user_input_ready.set()
            elif key.lower() == 'q':
                sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: task4_30.py <URL>")
        sys.exit(1)
        
    client = HTTPClientThreaded()
    
    # Запускаем поток для ввода пользователя
    input_thread = threading.Thread(target=client.user_input, daemon=True)
    input_thread.start()
    
    client.fetch_url(sys.argv[1])