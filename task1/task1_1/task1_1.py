import threading

def worker():
    """Функция, которую будет выполнять дочерний поток"""
    for i in range(10):
        print(f"Дочерний поток: строка {i + 1}")

def main():
    print("Задание 1: Создание потока")
    
    # Создаем и запускаем поток
    thread = threading.Thread(target=worker)
    thread.start()
    
    # Основной поток продолжает работу
    for i in range(10):
        print(f"Родительский поток: строка {i + 1}")
    
    # Ждем завершения дочернего потока (хотя в задании 1 это не требуется)
    thread.join()

if __name__ == "__main__":
    main()