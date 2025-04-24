import threading

def calculate_partial_sum(start, end, result, index):
    partial = 0.0
    for i in range(start, end):
        term = 1.0 / (2 * i + 1)
        if i % 2 == 1:
            term = -term
        partial += term
    result[index] = partial

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python task8_pi_threaded.py <пример 4 или 8 потока , можно даже с 2 до 16 потоков>")
        return
    
    num_threads = int(sys.argv[1])
    num_steps = 200000000
    steps_per_thread = num_steps // num_threads
    
    results = [0.0] * num_threads
    threads = []
    
    for i in range(num_threads):
        start = i * steps_per_thread
        end = (i + 1) * steps_per_thread if i != num_threads - 1 else num_steps
        t = threading.Thread(
            target=calculate_partial_sum,
            args=(start, end, results, i)
        )
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    pi = sum(results) * 4
    print(f"Calculated Pi: {pi:.15f}")

if __name__ == "__main__":
    main()