import threading
import time

# Флаг для безопасной остановки потока
stop_flag = False

def cleanup():
    """Функция очистки перед завершением потока"""
    print("Дочерний поток: выполняю cleanup перед завершением")

def worker():
    """Основная функция потока"""
    try:
        while not stop_flag:
            print("Дочерний поток работает...")
            time.sleep(0.3)
    finally:
        cleanup()  # Гарантированно выполнится при выходе

def main():
    global stop_flag
    print("Задание 5: Обработка завершения потока (безопасный вариант)")
    
    thread = threading.Thread(target=worker)
    thread.start()
    
    # Ждём 2 секунды перед остановкой
    time.sleep(2)
    
    # Устанавливаем флаг для остановки потока
    stop_flag = True
    
    # Ждём завершения потока
    thread.join()
    print("Родительский поток корректно завершил дочерний")

if __name__ == "__main__":
    main()