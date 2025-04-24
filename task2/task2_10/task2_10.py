import threading
import time
import random
import sys

# Константы
PHILOSOPHERS = 5  # Количество философов
FOOD_LIMIT = 50   # Лимит приемов пищи
MIN_DELAY = 0.1   # Минимальная задержка
MAX_DELAY = 0.5   # Максимальная задержка

# Вилки (мьютексы) и статусы философов
forks = [threading.Lock() for _ in range(PHILOSOPHERS)]
statuses = ['Д'] * PHILOSOPHERS  # Д - думает, Е - ест, Ж - ждет вилки
print_lock = threading.Lock()    # Для синхронизации вывода

def philosopher(philosopher_id):
    """Поведение философа"""
    left_fork = philosopher_id
    right_fork = (philosopher_id + 1) % PHILOSOPHERS
    
    # Четные берут сначала левую вилку, нечетные - правую
    first_fork, second_fork = (left_fork, right_fork) if philosopher_id % 2 == 0 else (right_fork, left_fork)
    
    for meal_count in range(1, FOOD_LIMIT + 1):
        # Фаза размышлений
        with print_lock:
            statuses[philosopher_id] = 'Д'
            update_status()
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        
        # Фаза ожидания вилок
        with print_lock:
            statuses[philosopher_id] = 'Ж'
            update_status()
        
        # Фаза еды
        with forks[first_fork], forks[second_fork]:
            with print_lock:
                statuses[philosopher_id] = 'Е'
                update_status()
                print(f"Философ {philosopher_id} ест ({meal_count} раз)")
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
    
    with print_lock:
        print(f"Философ {philosopher_id} завершил трапезу")

def update_status():
    """Обновление строки статусов"""
    sys.stdout.write('\r' + ' '.join(statuses) + ' ')
    sys.stdout.flush()

def main():
    print("Задача об обедающих философах")
    print("Статусы: Д - думает, Е - ест, Ж - ждет вилки\n")
    print("Начало симуляции...\n")
    
    # Создаем и запускаем потоки-философы
    philosophers = []
    for i in range(PHILOSOPHERS):
        philosopher_thread = threading.Thread(
            target=philosopher, 
            args=(i,),
            daemon=True
        )
        philosophers.append(philosopher_thread)
        philosopher_thread.start()
    
    # Ожидаем завершения всех философов
    for philosopher_thread in philosophers:
        philosopher_thread.join()
    
    print("\n\nВсе философы завершили трапезу")

if __name__ == "__main__":
    main()