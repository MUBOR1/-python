import threading
import time
import random

PHILOSOPHERS = 5
MEALS = 3  # Количество приемов пищи для каждого философа

class Philosopher(threading.Thread):
    def __init__(self, id, forks, condition):
        super().__init__()
        self.id = id
        self.left_fork = forks[id]
        self.right_fork = forks[(id + 1) % PHILOSOPHERS]
        self.condition = condition
        self.meals_eaten = 0

    def run(self):
        while self.meals_eaten < MEALS:
            self.think()
            self.eat()

    def think(self):
        print(f"Философ {self.id} размышляет")
        time.sleep(random.uniform(0.5, 1.5))

    def eat(self):
        with self.condition:
            while True:
                # Пытаемся взять обе вилки атомарно
                self.left_fork.acquire(blocking=False)
                acquired = self.right_fork.acquire(blocking=False)
                
                if acquired:
                    break  # Успешно взяли обе вилки
                
                # Если не получилось - освобождаем левую вилку и ждем
                self.left_fork.release()
                self.condition.wait()

        # Вилки успешно взяты - можно есть
        print(f"Философ {self.id} начал есть")
        time.sleep(random.uniform(0.2, 0.5))
        self.meals_eaten += 1

        # Освобождаем вилки
        self.left_fork.release()
        self.right_fork.release()
        
        with self.condition:
            self.condition.notify_all()

        print(f"Философ {self.id} закончил есть")

def main():
    forks = [threading.Lock() for _ in range(PHILOSOPHERS)]
    condition = threading.Condition()
    
    philosophers = [
        Philosopher(i, forks, condition) 
        for i in range(PHILOSOPHERS)
    ]

    for p in philosophers:
        p.start()

    for p in philosophers:
        p.join()

    print("Все философы наелись!")

if __name__ == "__main__":
    main()