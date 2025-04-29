import threading
import time

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.lock = threading.Lock()
    
    def add(self, data):
        with self.lock:
            new_node = Node(data)
            new_node.next = self.head
            self.head = new_node
    
    def display(self):
        with self.lock:
            current = self.head
            while current:
                print(current.data)
                current = current.next
    
    def bubble_sort(self):
        with self.lock:
            if not self.head:
                return
            
            changed = True
            while changed:
                changed = False
                current = self.head
                while current.next:
                    if current.data > current.next.data:
                        current.data, current.next.data = current.next.data, current.data
                        changed = True
                    current = current.next

def sort_thread(linked_list):
    while True:
        time.sleep(5)
        linked_list.bubble_sort()

def main():
    linked_list = LinkedList()
    sorter = threading.Thread(target=sort_thread, args=(linked_list,), daemon=True)
    sorter.start()
    
    while True:
        user_input = input("Введите строку (пустая для вывода): ")
        if not user_input:
            linked_list.display()
        else:
            # Разбиваем длинные строки
            for i in range(0, len(user_input), 80):
                linked_list.add(user_input[i:i+80])

if __name__ == "__main__":
    main()