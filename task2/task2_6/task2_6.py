import threading
import time
import sys

def sleep_print(s, length):
    time.sleep(length * 0.01)
    print(s)

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    else:
        lines = [line.strip() for line in sys.stdin if line.strip()]
    
    threads = []
    for line in lines:
        t = threading.Thread(target=sleep_print, args=(line, len(line)))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()