import threading

def worker(sem_child, sem_parent):
    for i in range(10):
        sem_child.acquire()  # Ждем разрешения
        print(f"Дочерний поток: строка {i + 1}")
        sem_parent.release()  # Разрешаем родительскому потоку

def main():
    # Семафоры (родитель начинает первым)
    sem_parent = threading.Semaphore(1)  # Родительский семафор
    sem_child = threading.Semaphore(0)   # Дочерний семафор
    
    thread = threading.Thread(target=worker, args=(sem_child, sem_parent))
    thread.start()
    
    for i in range(10):
        sem_parent.acquire()
        print(f"Родительский поток: строка {i + 1}")
        sem_child.release()  # Разрешаем дочернему потоку
    
    thread.join()

if __name__ == "__main__":
    main()