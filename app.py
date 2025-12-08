import tweepy
import os
import time
import random
from datetime import datetime, timedelta

# ======== Konfigurasi API ========
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

# ======== Folder & file ========
BASE_FOLDER = "queue_bot"
os.makedirs(BASE_FOLDER, exist_ok=True)
QUEUE_FILE = os.path.join(BASE_FOLDER, "queue.txt")
LOG_FILE = os.path.join(BASE_FOLDER, "log.txt")

for f in [QUEUE_FILE, LOG_FILE]:
    if not os.path.exists(f):
        open(f, "w", encoding="utf-8").close()

# ======== Fungsi ubah vokal + random kapitalisasi ========
def ubah_vokal_dan_random_caps(teks):
    vokal = "aiueoAIUEO"
    hasil = ""
    for c in teks:
        if c in vokal:
            c = 'i'
        if c.isalpha():
            c = c.upper() if random.choice([True, False]) else c.lower()
        hasil += c
    return hasil

# ======== Queue ========
def add_to_queue(username, user_id, tweet_id, teks):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}|{username}|{user_id}|{tweet_id}|{teks}\n")

def log_post(status, username, user_id, tweet_id, teks):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}|{status}|{username}|{user_id}|{tweet_id}|{teks}\n")

# ======== Ambil mention baru ========
last_seen_id = 1
def check_mentions():
    global last_seen_id
    try:
        mentions = api.mentions_timeline(since_id=last_seen_id, tweet_mode="extended")
        for mention in reversed(mentions):
            last_seen_id = mention.id
            parent_id = mention.in_reply_to_status_id
            if not parent_id:
                continue
            try:
                parent = api.get_status(parent_id, tweet_mode="extended")
                teks_baru = ubah_vokal_dan_random_caps(parent.full_text)
                add_to_queue(mention.user.screen_name, mention.user.id_str, parent.id, teks_baru)
            except Exception as e:
                print(f"[ERROR] Gagal ambil tweet parent @{mention.user.screen_name}: {e}")
    except Exception as e:
        print(f"[ERROR] Gagal cek mention: {e}")

# ======== Proses queue (posting baru) ========
def process_queue(max_batch=5):
    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        batch_count = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if batch_count >= max_batch:
                new_lines.append(line)
                continue
            try:
                timestamp, username, user_id, tweet_id, teks = line.split("|", 4)
                # Post tweet baru dengan mention + link
                postingan = f"@{username} {teks}\nLink asli: https://twitter.com/i/web/status/{tweet_id}"
                api.update_status(postingan)
                print(f"[OK] Berhasil posting @{username}")
                log_post("SUCCESS", username, user_id, tweet_id, teks)
                batch_count += 1
                time.sleep(random.uniform(1,3))
            except Exception as e:
                print(f"[ERROR] Gagal posting @{username}: {e}")
                new_lines.append(line)
        # Update queue
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            for l in new_lines:
                f.write(l + "\n")
    except Exception as e:
        print(f"[ERROR] Proses queue gagal: {e}")

# ======== Loop utama ========
print("[START] Bot berjalan...")
while True:
    try:
        check_mentions()
        process_queue(max_batch=5)
    except Exception as e:
        print(f"[ERROR] Loop utama: {e}")
    time.sleep(20)
