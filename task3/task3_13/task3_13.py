import threading

lock = threading.Lock()
cond = threading.Condition(lock)
parent_turn = True

def worker():
    global parent_turn
    for i in range(10):
        with cond:
            while parent_turn:
                cond.wait()
            print(f"Дочерний поток: строка {i + 1}")
            parent_turn = True
            cond.notify()

def main():
    global parent_turn
    thread = threading.Thread(target=worker)
    thread.start()
    
    for i in range(10):
        with cond:
            while not parent_turn:
                cond.wait()
            print(f"Родительский поток: строка {i + 1}")
            parent_turn = False
            cond.notify()
    
    thread.join()