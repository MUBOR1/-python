import threading
import signal
import sys
import time
from itertools import count

stop_flag = False
progress_interval = 1_000_000  # Выводить прогресс каждые 1M итераций

def signal_handler(sig, frame):
    global stop_flag
    stop_flag = True
    print("\nПолучен сигнал прерывания, завершение вычислений...")

def calculate_partial_sum(thread_id, result):
    global stop_flag
    partial = 0.0
    iterations = 0
    
    for i in count(start=thread_id, step=4):
        if stop_flag:
            break
            
        # Вычисляем 4 члена ряда за одну итерацию (ускорение в ~4 раза)
        term1 = 1.0 / (2*i + 1)
        term2 = 1.0 / (2*(i+1) + 1)
        term3 = 1.0 / (2*(i+2) + 1)
        term4 = 1.0 / (2*(i+3) + 1)
        
        partial += term1 - term2 + term3 - term4
        iterations += 4
        
        # Вывод прогресса для первого потока
        if thread_id == 0 and iterations % progress_interval == 0:
            current_pi = partial * 4  # Частичное приближение
            print(f"Прогресс: {iterations:,} итераций, текущее π ≈ {current_pi:.12f}", end='\r')
    
    result[thread_id] = (partial, iterations)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    print("Вычисление π. Нажмите Ctrl+C для остановки...")
    print("Прогресс будет отображаться ниже:")
    
    num_threads = 4
    results = [(0.0, 0)] * num_threads
    threads = []
    
    # Засекаем время выполнения
    start_time = time.time()
    
    for i in range(num_threads):
        t = threading.Thread(
            target=calculate_partial_sum,
            args=(i, results)
        )
        threads.append(t)
        t.daemon = True  # Потоки завершатся при выходе из main
        t.start()
    
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_flag = True
    
    for t in threads:
        t.join()
    
    total_sum = sum(r[0] for r in results)
    total_steps = sum(r[1] for r in results)
    pi = total_sum * 4
    elapsed = time.time() - start_time
    
    print(f"\n\nРезультат:")
    print(f"Всего итераций: {total_steps:,}")
    print(f"Вычисленное π: {pi:.15f}")
    print(f"Время выполнения: {elapsed:.2f} сек")
    print(f"Скорость: {total_steps/elapsed:,.0f} итераций/сек")

if __name__ == "__main__":
    main()