import os
import sys
import shutil
import threading

def get_script_dir():
    """Возвращает директорию, где находится текущий скрипт"""
    return os.path.dirname(os.path.abspath(__file__))

def copy_file(src, dst):
    try:
        shutil.copy2(src, dst)
        print(f"Copied: {src} -> {dst}")
    except Exception as e:
        print(f"Error copying {src}: {e}")

def process_dir(src_root, dst_root):
    """Рекурсивная обработка директории"""
    for root, dirs, files in os.walk(src_root):
        rel_path = os.path.relpath(root, src_root)
        dst_dir = os.path.join(dst_root, rel_path)
        
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        
        threads = []
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_dir, file)
            t = threading.Thread(target=copy_file, args=(src_file, dst_file))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()

def main():
    if len(sys.argv) != 3:
        script_dir = get_script_dir()
        print("Usage: python task2_7.py <source> <destination>")
        print(f"Current script directory: {script_dir}")
        print("Example:")
        print(f'  python task2_7.py "source_dir" "destination_dir"')
        print(f'  python task2_7.py "C:\\My Source" "C:\\My Destination"')
        sys.exit(1)

    src = os.path.normpath(sys.argv[1])
    dst = os.path.normpath(sys.argv[2])

    # Если пути относительные, преобразуем их в абсолютные относительно директории скрипта
    if not os.path.isabs(src):
        src = os.path.join(get_script_dir(), src)
    if not os.path.isabs(dst):
        dst = os.path.join(get_script_dir(), dst)

    if not os.path.exists(src):
        print(f"Error: Source path '{src}' does not exist")
        sys.exit(1)

    if src == dst:
        print("Error: Source and destination paths are the same")
        sys.exit(1)

    print(f"Copying from: {src}")
    print(f"Copying to: {dst}")
    process_dir(src, dst)
    print("Copying completed!")

if __name__ == "__main__":
    main()