from threading import RLock

class RWLinkedList:
    def __init__(self):
        self.head = None
        self.rw_lock = RLock()
    
    def add(self, data):
        with self.rw_lock:
            new_node = ThreadSafeNode(data)
            new_node.next = self.head
            self.head = new_node
    
    def display(self):
        with self.rw_lock:  # Блокировка для чтения
            current = self.head
            while current:
                print(current.data)
                current = current.next
    
    def bubble_sort(self):
        with self.rw_lock:  # Эксклюзивная блокировка
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