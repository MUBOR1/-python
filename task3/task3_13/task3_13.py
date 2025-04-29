import threading

def worker(cond, parent_turn):
    for i in range(10):
        with cond:
            while parent_turn[0]:  # Ждём, пока не придёт наша очередь
                cond.wait()
            print(f"Дочерний поток: строка {i + 1}")
            parent_turn[0] = True  # Передаём очередь родителю
            cond.notify()

def main():
    lock = threading.Lock()
    cond = threading.Condition(lock)
    parent_turn = [True]  # Начинает родительский поток

    thread = threading.Thread(target=worker, args=(cond, parent_turn))
    thread.start()

    for i in range(10):
        with cond:
            while not parent_turn[0]:  # Ждём свою очередь
                cond.wait()
            print(f"Родительский поток: строка {i + 1}")
            parent_turn[0] = False  # Передаём очередь дочернему потоку
            cond.notify()

    thread.join()

if __name__ == "__main__":
    main()