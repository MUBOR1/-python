# message_queue.py
import threading
from collections import deque
from threading import Semaphore
import time

class MessageQueue:
    def __init__(self):
        self.queue = deque()
        self.max_size = 10
        self.max_msg_length = 80
        self.active = True
        
        # Семафоры для синхронизации
        self.mutex = Semaphore(1)          # Бинарный семафор для доступа к очереди
        self.items_available = Semaphore(0) # Количество доступных элементов
        self.spaces_available = Semaphore(self.max_size) # Количество свободных мест
        
    def put(self, msg):
        if not self.active:
            return 0
            
        # Обрезаем сообщение до максимальной длины
        msg = str(msg)[:self.max_msg_length]
        msg_length = len(msg)
        
        # Если очередь отключена во время ожидания
        if not self.spaces_available.acquire(timeout=0.1):
            return 0
            
        if not self.active:
            self.spaces_available.release()
            return 0
            
        self.mutex.acquire()
        try:
            self.queue.append(msg)
        finally:
            self.mutex.release()
        
        self.items_available.release()
        return msg_length
        
    def get(self, buf_size=256):
        if not self.active and not self.items_available._value:
            return ""
            
        if not self.items_available.acquire(timeout=0.1):
            return ""
            
        if not self.active and not self.queue:
            self.items_available.release()
            return ""
            
        self.mutex.acquire()
        try:
            msg = self.queue.popleft()
        finally:
            self.mutex.release()
        
        self.spaces_available.release()
        
        # Возвращаем сообщение (аналог копирования в буфер)
        return msg[:buf_size]
        
    def drop(self):
        self.active = False
        # Разблокируем все ожидающие потоки
        while self.spaces_available._value < self.max_size:
            self.spaces_available.release()
        while self.items_available._value > 0:
            self.items_available.release()
            
    def destroy(self):
        self.drop()
        self.queue.clear()

# Тестирование с производителями и потребителями
def producer(queue, id, count=5):
    for i in range(count):
        msg = f"Message {i} from producer {id}"
        length = queue.put(msg)
        print(f"Producer {id} sent: {msg[:20]}... (length: {length})")
        time.sleep(0.5)
    print(f"Producer {id} finished")

def consumer(queue, id):
    while True:
        msg = queue.get()
        if not msg and not queue.active:
            break
        if msg:
            print(f"Consumer {id} received: {msg[:20]}... (length: {len(msg)})")
        time.sleep(0.3)
    print(f"Consumer {id} finished")

if __name__ == "__main__":
    q = MessageQueue()
    
    # Создаем производителей и потребителей
    producers = [
        threading.Thread(target=producer, args=(q, 1)),
        threading.Thread(target=producer, args=(q, 2))
    ]
    
    consumers = [
        threading.Thread(target=consumer, args=(q, 1)),
        threading.Thread(target=consumer, args=(q, 2))
    ]
    
    # Запускаем все потоки
    for p in producers:
        p.start()
    for c in consumers:
        c.start()
    
    # Ждем завершения производителей
    for p in producers:
        p.join()
    
    # Даем время на обработку оставшихся сообщений
    time.sleep(1)
    
    # Завершаем работу очереди
    q.drop()
    
    # Ждем завершения потребителей
    for c in consumers:
        c.join()
    
    # Уничтожаем очередь
    q.destroy()
    print("Queue destroyed")