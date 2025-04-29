# Для Linux/macOS (в Windows используйте multiprocessing.Semaphore)
from multiprocessing import Process, Semaphore
import sys

def worker(sem1, sem2):
    for i in range(10):
        sem1.acquire()
        print("Дочерний процесс:", i+1)
        sem2.release()

if __name__ == "__main__":
    sem_parent = Semaphore(1)
    sem_child = Semaphore(0)
    
    p = Process(target=worker, args=(sem_child, sem_parent))
    p.start()
    
    for i in range(10):
        sem_parent.acquire()
        print("Родительский процесс:", i+1)
        sem_child.release()
    
    p.join()