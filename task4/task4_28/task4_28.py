# http_client_select.py
import sys
import socket
import select
import urllib.parse

class HTTPClient:
    def __init__(self):
        self.screen_lines = 0
        self.paused = False
        
    def fetch_url(self, url):
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc
        path = parsed.path if parsed.path else '/'
        
        if not host:
            print("Неверный URL: отсутствует хост")
            return
            
        # Устанавливаем соединение
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, 80))
            
            # Отправляем HTTP-запрос
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            s.send(request.encode())
            
            # Читаем ответ
            response = b''
            while True:
                readable, _, _ = select.select([s], [], [], 1)
                if not readable:
                    continue
                    
                data = s.recv(4096)
                if not data:
                    break
                    
                # Показываем данные постранично
                self.display_data(data.decode('utf-8', errors='ignore'))
                
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            s.close()
            
    def display_data(self, text):
        for char in text:
            if self.screen_lines >= 25 and not self.paused:
                print("\nPress space to scroll down...")
                self.paused = True
                
            if self.paused:
                # Ждем ввода пользователя
                rlist, _, _ = select.select([sys.stdin], [], [])
                if rlist:
                    key = sys.stdin.read(1)
                    if key == ' ':
                        self.screen_lines = 0
                        self.paused = False
                    elif key.lower() == 'q':
                        sys.exit(0)
                continue
                
            print(char, end='', flush=True)
            if char == '\n':
                self.screen_lines += 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python http_client_select.py <URL>")
        sys.exit(1)
        
    client = HTTPClient()
    client.fetch_url(sys.argv[1])