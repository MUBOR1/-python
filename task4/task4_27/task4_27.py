# tcp_proxy.py
import socket
import threading
import sys
import select

class TCPProxy:
    def __init__(self, listen_port, target_host, target_port):
        self.listen_port = listen_port
        self.target_host = target_host
        self.target_port = target_port
        self.running = False
        
    def handle_client(self, client_socket):
        try:
            # Устанавливаем соединение с целевым сервером
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((self.target_host, self.target_port))
            
            # Получаем первый пакет от клиента
            data = client_socket.recv(4096)
            if not data:
                return
                
            # Модифицируем HTTP-заголовок
            request = self.modify_http_request(data.decode('utf-8'))
            target_socket.send(request.encode())
            
            sockets = [client_socket, target_socket]
            
            while self.running:
                readable, _, exceptional = select.select(sockets, [], sockets, 1)
                
                if exceptional:
                    break
                    
                for sock in readable:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            break
                            
                        if sock is client_socket:
                            target_socket.sendall(data)
                        else:
                            client_socket.sendall(data)
                    except:
                        break
                        
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            client_socket.close()
            target_socket.close()
            
    def modify_http_request(self, request):
        """Исправляем HTTP-заголовки для корректной работы"""
        lines = request.split('\r\n')
        if not lines:
            return request
            
        # Изменяем строку запроса и заголовок Host
        modified_lines = []
        for line in lines:
            if line.startswith('GET') or line.startswith('POST') or line.startswith('HEAD'):
                parts = line.split()
                if len(parts) >= 2:
                    modified_lines.append(f"{parts[0]} {parts[1]} HTTP/1.1")
            elif line.startswith('Host:'):
                modified_lines.append(f"Host: {self.target_host}")
            elif line.strip():
                modified_lines.append(line)
                
        return '\r\n'.join(modified_lines) + '\r\n\r\n'
            
    def start(self):
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.listen_port))
        server_socket.listen(10)
        
        print(f"Сервер слушает порт {self.listen_port}, перенаправляет на {self.target_host}:{self.target_port}")
        
        try:
            while self.running:
                client_socket, addr = server_socket.accept()
                print(f"Принято соединение от {addr[0]}:{addr[1]}")
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("Остановка сервера...")
        finally:
            self.running = False
            server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python task4_27.py <listen_port> <target_host> <target_port>")
        sys.exit(1)
        
    listen_port = int(sys.argv[1])
    target_host = sys.argv[2]
    target_port = int(sys.argv[3])
    
    proxy = TCPProxy(listen_port, target_host, target_port)
    proxy.start()