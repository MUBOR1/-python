def bubble_sort_visual(linked_list):
    while True:
        time.sleep(1)  # Задержка между шагами
        with linked_list.head_lock:
            if not linked_list.head or not linked_list.head.next:
                continue
            
            # Блокируем три узла для перестановки
            a = linked_list.head
            b = a.next
            c = b.next if b else None
            
            with a.lock:
                with b.lock:
                    if a.data > b.data:
                        a.data, b.data = b.data, a.data
                        print("Перестановка:", a.data, "<->", b.data)
            
            # Продолжаем для остальных узлов
            prev = b
            current = c
            
            while current:
                with prev.lock:
                    with current.lock:
                        next_node = current.next
                        if next_node:
                            with next_node.lock:
                                if current.data > next_node.data:
                                    current.data, next_node.data = next_node.data, current.data
                                    print("Перестановка:", current.data, "<->", next_node.data)
                prev = current
                current = next_node