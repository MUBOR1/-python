# widget_factory.py
import threading
import time
from threading import Semaphore

class WidgetFactory:
    def __init__(self):
        self.semaphore_a = Semaphore(0)
        self.semaphore_b = Semaphore(0)
        self.semaphore_c = Semaphore(0)
        self.semaphore_module = Semaphore(0)
        self.widget_count = 0
        self.lock = threading.Lock()

    def produce_part_a(self):
        time.sleep(1)
        with self.lock:
            print("Деталь A изготовлена")
        self.semaphore_a.release()

    def produce_part_b(self):
        time.sleep(2)
        with self.lock:
            print("Деталь B изготовлена")
        self.semaphore_b.release()

    def assemble_module(self):
        self.semaphore_a.acquire()
        self.semaphore_b.acquire()
        time.sleep(0.5)  # Время сборки модуля
        with self.lock:
            print("Модуль собран из A и B")
        self.semaphore_module.release()

    def produce_part_c(self):
        time.sleep(3)
        with self.lock:
            print("Деталь C изготовлена")
        self.semaphore_c.release()

    def assemble_widget(self):
        self.semaphore_module.acquire()
        self.semaphore_c.acquire()
        time.sleep(1)  # Время сборки винтика
        with self.lock:
            self.widget_count += 1
            print(f"Винтик #{self.widget_count} собран из модуля и C")

    def run_production(self, num_widgets):
        threads = []
        
        for _ in range(num_widgets):
            # Производство деталей
            threads.append(threading.Thread(target=self.produce_part_a))
            threads.append(threading.Thread(target=self.produce_part_b))
            threads.append(threading.Thread(target=self.produce_part_c))
            
            # Сборка модуля
            threads.append(threading.Thread(target=self.assemble_module))
            
            # Сборка винтика
            threads.append(threading.Thread(target=self.assemble_widget))
        
        for thread in threads:
            thread.start()
            
        for thread in threads:
            thread.join()

if __name__ == "__main__":
    factory = WidgetFactory()
    factory.run_production(3)  # Произведем 3 винтика