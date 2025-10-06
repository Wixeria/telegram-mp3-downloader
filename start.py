import os
import re
import asyncio
import json
from telethon import TelegramClient
from tqdm import tqdm
from colorama import init, Fore

init(autoreset=True)

config_path = "config.json"
if not os.path.exists(config_path):
    default_config = {
        "api_id": 123456,
        "api_hash": "12345678901234567890123456789012",
        "phone_number": "+1234567890",
        "downloads_folder": "downloads",
        "concurrent_downloads": 5
    }
    with open(config_path, "w") as f:
        json.dump(default_config, f, indent=4)
    print(Fore.YELLOW + "Created default config.json. Please edit it with your API info and rerun.")
    exit()

with open(config_path, "r") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
phone_number = config["phone_number"]
base_folder = os.path.join(os.getcwd(), config.get("downloads_folder", "downloads"))
CONCURRENT_DOWNLOADS = config.get("concurrent_downloads", 5)

os.makedirs(base_folder, exist_ok=True)

client = TelegramClient('cookies', api_id, api_hash)

log_file = os.path.join(base_folder, "download.log")
def log(message):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def sanitize_filename(filename):
    filename = re.sub(r'[\/:*?"<>|]', '_', filename)
    return filename.strip()

def progress_callback(current, total, bar=None):
    if bar:
        bar.update(current - bar.n)
        if current == total:
            bar.close()

async def download_message(message, download_folder, semaphore, overall_bar):
    async with semaphore:
        filename = sanitize_filename(message.file.name)
        save_path = os.path.join(download_folder, filename)

        if os.path.exists(save_path) and os.path.getsize(save_path) == message.document.size:
            print(Fore.CYAN + f"Skipping {filename}, already exists.")
            log(f"Skipped: {filename}")
            overall_bar.update(1)
            return 0

        existing_size = os.path.getsize(save_path) if os.path.exists(save_path) else 0
        total_size = message.document.size
        bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=filename[:30])
        bar.update(existing_size)

        retries = 3
        logged = False
        for attempt in range(1, retries + 1):
            try:
                await message.download_media(
                    file=save_path,
                    progress_callback=lambda cur, tot: progress_callback(cur, tot, bar)
                )
                print(Fore.GREEN + f"✅ Downloaded: {filename}")
                if not logged:
                    log(f"Downloaded: {filename}")
                    logged = True
                overall_bar.update(1)
                return 1
            except Exception as e:
                print(Fore.RED + f"❌ Error downloading {filename} (Attempt {attempt}/{retries}): {e}")
                if not logged:
                    log(f"Error: {filename} - {e}")
                    logged = True
                if attempt == retries:
                    overall_bar.update(1)
                    return 0

async def main():
    print(Fore.YELLOW + "Starting Telegram downloader...")
    await client.start(phone_number)

    targets = input("Enter chat usernames/IDs (comma separated for multiple chats): ").split(",")
    targets = [t.strip() for t in targets if t.strip()]
    if not targets:
        print(Fore.RED + "No chats provided. Exiting.")
        return

    max_files_input = input("Enter max number of files to download per chat (0 for all): ").strip()
    try:
        max_files = int(max_files_input)
        if max_files < 0:
            max_files = 0
    except ValueError:
        max_files = 0

    semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS)

    for target in targets:
        try:
            chat = await client.get_entity(target)
        except Exception as e:
            print(Fore.RED + f"Failed to get chat {target}: {e}")
            continue

        chat_folder_name = chat.username or str(chat.id)
        chat_folder_name = sanitize_filename(chat_folder_name)
        download_folder = os.path.join(base_folder, chat_folder_name)
        os.makedirs(download_folder, exist_ok=True)

        total_mp3_files = 0
        async for message in client.iter_messages(chat):
            if message.document and message.file.name and message.file.name.lower().endswith(".mp3"):
                total_mp3_files += 1
                if max_files and total_mp3_files >= max_files:
                    break

        if total_mp3_files == 0:
            print(Fore.CYAN + f"No .mp3 files found in '{chat_folder_name}'\n")
            continue

        print(Fore.MAGENTA + f"\nDownloading {total_mp3_files} files from chat: {chat_folder_name}")
        overall_bar = tqdm(total=total_mp3_files, desc="Total progress", unit="file")

        tasks = []
        count = 0
        async for message in client.iter_messages(chat):
            if message.document and message.file.name and message.file.name.lower().endswith(".mp3"):
                tasks.append(download_message(message, download_folder, semaphore, overall_bar))
                count += 1
                if max_files and count >= max_files:
                    break

        if tasks:
            await asyncio.gather(*tasks)
        overall_bar.close()
        print(Fore.YELLOW + f"Finished downloading from '{chat_folder_name}'\n")

    client.loop.run_until_complete(main())