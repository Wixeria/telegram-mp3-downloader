# Telegram MP3 Downloader

A fast, feature-rich Telegram **.mp3 downloader** built with [Telethon](https://github.com/LonamiWebs/Telethon).  
Downloads audio files from chats or channels with **resume support, logging, progress bars, per-chat subfolders, and concurrency control**.  

---

## ✨ Features
- 📂 Auto subfolders by chat name  
- 📥 Resume partially downloaded files  
- ⚡ Concurrent downloads with configurable limit  
- 🎵 Filters for `.mp3` files only  
- 🧮 Overall and per-file progress bars (via `tqdm`)  
- 📜 Logging (`download.log`) of successes, skips, and errors  
- 🛠 Configurable via `config.json`  
- 💻 User-friendly CLI

---

## 📦 Requirements

- Python **3.9+** (tested on Python 3.13)  
- Dependencies listed in `requirements.txt`:  
  ```txt
  telethon>=1.41.0
  tqdm>=4.66.0
  colorama>=0.4.6
Install them with:
```python
pip install -r requirements.txt
```
---

## ⚙️ Setup

1. Clone the repository:
```git
git clone https://github.com/wixeria/telegram-mp3-downloader.git
cd telegram-mp3-downloader
```

2. Install dependencies:
```python
python -m pip install -r requirements.txt
```

3. Create your config.json (it will be auto-created if missing):
```json
{
    "api_id": 123456,
    "api_hash": "12345678901234567890123456789012",
    "phone_number": "+1234567890",
    "downloads_folder": "downloads",
    "concurrent_downloads": 5
}
```

- api_id / api_hash: Get from [here](my.telegram.org).
- phone_number: Your Telegram account phone number.
- downloads_folder: Root folder for saving files.
- concurrent_downloads: Number of files to download at once.

---

## 🚀 Usage

Run the downloader:
```python
python start.py
```
- The script will ask for a chat username or ID.
- It will then ask how many files you want to download (0 = all).
- Files will be saved into rootfolder_name/chat_name/.

Example:
```python
Enter chat username or chat ID: my_fav_music
Enter max number of files to download per chat (0 for all): 10
```
Output:
```yaml
Downloading 10 files from chat: my_fav_music
Team Sleep - Blvd. Nights (Amen Re...: 100%|█████████| 17.4M/17.4M [01:29<00:00, 194kB/s]
✅ Downloaded: Team Sleep - Blvd. Nights.mp3
```

----

## 📝 Logging

- All events are logged to download.log:
```yaml
[2025-10-06 01:32:10] Downloaded: Team Sleep - Blvd. Nights.mp3
[2025-10-06 01:33:45] Skipped: Song.mp3 (already exists)
[2025-10-06 01:34:12] Error: BrokenFile.mp3 - Connection reset
```

---

## 📜 License

MIT License – free to use, modify, and share.

----

## 💡 Credits

Built with [Telethon](https://github.com/LonamiWebs/Telethon), [tqdm](https://github.com/tqdm/tqdm), and [colorama](https://github.com/tartley/colorama).
