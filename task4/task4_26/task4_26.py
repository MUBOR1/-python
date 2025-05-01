# message_queue_cv.py
import threading
import time
from collections import deque

class MessageQueueCV:
    def __init__(self):
        self.queue = deque()
        self.max_size = 10
        self.max_msg_length = 80
        self.active = True
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)
        
    def put(self, msg):
        with self.lock:
            # Ожидаем, пока не появится свободное место или очередь не станет неактивной
            while len(self.queue) >= self.max_size and self.active:
                self.not_full.wait()
            
            if not self.active:
                return 0
                
            # Обрезаем сообщение и преобразуем в строку
            msg_str = str(msg)[:self.max_msg_length]
            self.queue.append(msg_str)
            self.not_empty.notify()
            return len(msg_str)
            
    def get(self, buf_size=256):
        with self.lock:
            # Ожидаем, пока не появится сообщение или очередь не станет неактивной
            while len(self.queue) == 0 and self.active:
                self.not_empty.wait()
            
            if not self.active and len(self.queue) == 0:
                return ""
                
            msg = self.queue.popleft()
            self.not_full.notify()
            
            # Возвращаем сообщение (обрезаем до buf_size)
            return msg[:buf_size]
            
    def drop(self):
        with self.lock:
            self.active = False
            self.not_empty.notify_all()
            self.not_full.notify_all()
            
    def destroy(self):
        self.drop()
        with self.lock:
            self.queue.clear()

# Тестирование с производителями и потребителями
def producer(queue, id, count=5):
    for i in range(count):
        msg = f"Сообщение {i} от производителя {id}"
        length = queue.put(msg)
        print(f"Производитель {id} отправил: {msg[:20]}... (длина: {length})")
        time.sleep(0.5)
    print(f"Производитель {id} завершил работу")

def consumer(queue, id):
    while True:
        msg = queue.get()
        if not msg and not queue.active:
            break
        if msg:
            print(f"Потребитель {id} получил: {msg[:20]}... (длина: {len(msg)})")
        time.sleep(0.3)
    print(f"Потребитель {id} завершил работу")

if __name__ == "__main__":
    queue = MessageQueueCV()
    
    # Создаем производителей и потребителей
    producers = [
        threading.Thread(target=producer, args=(queue, 1)),
        threading.Thread(target=producer, args=(queue, 2))
    ]
    
    consumers = [
        threading.Thread(target=consumer, args=(queue, 1)),
        threading.Thread(target=consumer, args=(queue, 2))
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
    queue.drop()
    
    # Ждем завершения потребителей
    for c in consumers:
        c.join()
    
    # Уничтожаем очередь
    queue.destroy()
    print("Очередь уничтожена")