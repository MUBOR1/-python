import threading
import time

class ThreadSafeNode:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.lock = threading.Lock()

    def __str__(self):
        return str(self.data)

class ConcurrentLinkedList:
    def __init__(self):
        self.head = None
        self.head_lock = threading.Lock()
    
    def add(self, data):
        """Потокобезопасное добавление в начало списка"""
        new_node = ThreadSafeNode(data)
        with self.head_lock:
            new_node.next = self.head
            self.head = new_node
    
    def bubble_sort_step(self):
        """Выполняет один шаг сортировки с блокировкой трёх узлов"""
        with self.head_lock:
            if not self.head or not self.head.next:
                return False
            
            # Блокируем первые три узла
            first = self.head
            second = first.next
            third = second.next if second else None
            
            with first.lock:
                with second.lock:
                    changed = False
                    
                    # Сравниваем первые два узла
                    if first.data > second.data:
                        first.data, second.data = second.data, first.data
                        changed = True
                    
                    if not third:
                        return changed
                    
                    # Блокируем третий узел для сравнения
                    with third.lock:
                        if second.data > third.data:
                            second.data, third.data = third.data, second.data
                            changed = True
                    
                    return changed
    
    def bubble_sort_full(self):
        """Полная сортировка списка"""
        sorted = False
        while not sorted:
            sorted = not self.bubble_sort_step()
            time.sleep(0.1)  # Для визуализации процесса
    
    def display(self):
        """Потокобезопасный вывод списка"""
        with self.head_lock:
            current = self.head
            while current:
                with current.lock:
                    print(current.data, end=" -> ")
                    current = current.next
            print("None")

# Пример использования
if __name__ == "__main__":
    linked_list = ConcurrentLinkedList()
    
    # Добавляем элементы в нескольких потоках
    def add_items(items):
        for item in items:
            linked_list.add(item)
            time.sleep(0.01)
    
    adder1 = threading.Thread(target=add_items, args=([3, 1, 4],))
    adder2 = threading.Thread(target=add_items, args=([1, 5, 9],))
    
    adder1.start()
    adder2.start()
    adder1.join()
    adder2.join()
    
    print("До сортировки:")
    linked_list.display()
    
    # Сортировка в отдельном потоке
    sorter = threading.Thread(target=linked_list.bubble_sort_full)
    sorter.start()
    
    # Вывод промежуточных результатов
    for _ in range(5):
        time.sleep(0.3)
        linked_list.display()
    
    sorter.join()
    
    print("После сортировки:")
    linked_list.display()