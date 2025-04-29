def sort_with_rwlock(linked_list):
    while True:
        time.sleep(5)
        # Получаем эксклюзивный доступ для сортировки
        with linked_list.rw_lock:
            print("\nНачало сортировки...")
            linked_list.bubble_sort()
            print("Сортировка завершена. Текущий список:")
            linked_list.display()