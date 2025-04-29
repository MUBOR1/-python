import threading

mutex_parent = threading.Lock()
mutex_child = threading.Lock()

def worker():
    for i in range(10):
        mutex_child.acquire()
        print(f"Дочерний поток: строка {i + 1}")
        mutex_parent.release()

def main():
    mutex_child.acquire()  # Блокируем сначала дочерний поток
    
    thread = threading.Thread(target=worker)
    thread.start()
    
    for i in range(10):
        mutex_parent.acquire()
        print(f"Родительский поток: строка {i + 1}")
        mutex_child.release()
    
    thread.join()

if __name__ == "__main__":
    main()