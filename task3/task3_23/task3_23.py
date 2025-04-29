import threading
import time

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class SortedList:
    def __init__(self):
        self.head = None
        self.lock = threading.Lock()
    
    def insert(self, data):
        time.sleep(len(data) * 0.01)  # Задержка пропорциональна длине строки
        with self.lock:
            new_node = Node(data)
            if not self.head or len(data) < len(self.head.data):
                new_node.next = self.head
                self.head = new_node
            else:
                current = self.head
                while current.next and len(data) >= len(current.next.data):
                    current = current.next
                new_node.next = current.next
                current.next = new_node

def worker(data, sorted_list):
    sorted_list.insert(data)

def main():
    strings = ["короткая", "средняя строка", "очень длинная строка для теста"]
    sorted_list = SortedList()
    threads = []
    
    for s in strings:
        t = threading.Thread(target=worker, args=(s, sorted_list))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Вывод отсортированного списка
    current = sorted_list.head
    while current:
        print(current.data)
        current = current.next

if __name__ == "__main__":
    main()