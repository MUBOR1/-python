import threading

def worker():
    """Функция для дочернего потока"""
    for i in range(10):
        print(f"Дочерний поток: строка {i + 1}")

def main():
    print("Задание 2: Ожидание потока")
    
    thread = threading.Thread(target=worker)
    thread.start()
    
    # Основной поток ждет завершения дочернего
    thread.join()
    
    # После завершения дочернего потока
    for i in range(10):
        print(f"Родительский поток: строка {i + 1}")

if __name__ == "__main__":
    main()