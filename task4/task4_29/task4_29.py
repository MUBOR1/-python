# http_client_aio.py
import sys
import asyncio
import aiohttp
from urllib.parse import urlparse

class HTTPClientAIO:
    def __init__(self):
        self.screen_lines = 0
        self.paused = False
        
    async def fetch_url(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    # Читаем ответ порциями
                    while True:
                        chunk = await response.content.read(4096)
                        if not chunk:
                            break
                            
                        text = chunk.decode('utf-8', errors='ignore')
                        self.display_data(text)
                        
        except Exception as e:
            print(f"Ошибка: {e}")
            
    def display_data(self, text):
        for char in text:
            if self.screen_lines >= 25 and not self.paused:
                print("\nPress space to scroll down (q to quit)...", end='', flush=True)
                self.paused = True
                
            if self.paused:
                # Используем синхронный ввод, так как asyncio не поддерживает stdin в Windows
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode()
                    if key == ' ':
                        self.screen_lines = 0
                        self.paused = False
                    elif key.lower() == 'q':
                        sys.exit(0)
                continue
                
            print(char, end='', flush=True)
            if char == '\n':
                self.screen_lines += 1

async def main():
    if len(sys.argv) != 2:
        print("Использование: python task4_29.py <URL>")
        sys.exit(1)
        
    client = HTTPClientAIO()
    await client.fetch_url(sys.argv[1])

if __name__ == "__main__":
    # Для работы в Windows нужно использовать специальный цикл событий
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())