import threading

def worker(text_sequence, thread_num):
    """Функция для дочерних потоков"""
    for i, text in enumerate(text_sequence):
        print(f"Поток {thread_num}: {text} (сообщение {i + 1})")

def main():
    print("Задание 3: Параметры потока")
    
    # Разные последовательности для каждого потока
    sequences = [
        ["Привет", "Пока", "Как дела?"],
        ["Яблоко", "Банан", "Апельсин"],
        ["Красный", "Зеленый", "Синий"],
        ["Собака", "Кошка", "Попугай"]
    ]
    
    threads = []
    
    for i in range(4):
        thread = threading.Thread(
            target=worker,
            args=(sequences[i], i + 1)
        )
        threads.append(thread)
        thread.start()
    
    # Ожидаем завершения всех потоков
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()