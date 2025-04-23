import threading
import time

# Флаг для остановки потока
stop_flag = False

def worker():
    """Бесконечный цикл в дочернем потоке"""
    global stop_flag
    while not stop_flag:
        print("Дочерний поток работает...")
        time.sleep(0.3)
    print("Дочерний поток завершается корректно")

def main():
    global stop_flag
    print("Задание 4: Принудительное завершение потока (с флагом)")
    
    thread = threading.Thread(target=worker)
    thread.start()
    
    # Ждем 2 секунды
    time.sleep(2)
    
    # Устанавливаем флаг для остановки
    stop_flag = True
    
    # Ждем, пока поток завершится
    thread.join()
    print("Родительский поток завершил дочерний")

if __name__ == "__main__":
    main()