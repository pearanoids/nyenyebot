import time
import random
import tweepy
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

# ============================================================
# KONFIGURASI AKUN BOT
# ============================================================


BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAEwvawEAAAAA48x7h9TUmO03p1DWXNeca1idYJs%3DqkLh2xwwW9fAAGi3goA9n2kj4SOZh9CaUyY1sSb76WEAgWzsTz"
API_KEY = "c1VvzfhWsMYHiT9t9y7MMKGMc"
API_SECRET = "mcaZNlj8UWObae7lOCICAGdQPPCX0t2zip3JV1WtYuRZMYYtyq"
ACCESS_TOKEN = "1504365905111035905-YuzXxZkS7Fp9PKuQ5WkzH7Upvf2p6v"
ACCESS_TOKEN_SECRET = "iAwbusG6H3mkw6PqtnkfML60K63ewGHVRnnSCBJoiom3H"

DELAY_MENIT = 2
CHECK_INTERVAL = DELAY_MENIT * 60

# ============================================================
# AUTENTIKASI
# ============================================================

print(Fore.CYAN + "[INIT] Memulai proses autentikasi...")
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)
print(Fore.GREEN + "[SUCCESS] Autentikasi berhasil.\n")

# ============================================================
# VARIABEL SISTEM
# ============================================================

processed_ids = set()
queue = []

# ============================================================
# FUNGSI UTILITAS
# ============================================================

def timestamp():
    return Fore.YELLOW + datetime.now().strftime("[%H:%M:%S] ") + Style.RESET_ALL

def stylize_text(text):
    vowels = "aiueoAIUEO"
    out = []
    for c in text:
        if c in vowels:
            out.append("i" if c.islower() else "I")
        else:
            out.append(c)
    out = "".join(out)

    final = []
    for c in out:
        final.append(c.upper() if random.random() < 0.25 else c.lower())
    return "".join(final)

def fetch_parent_text(tweet):
    if tweet.referenced_tweets:
        try:
            parent_id = tweet.referenced_tweets[0].id
            parent = client.get_tweet(parent_id, tweet_fields=["text"]).data
            return parent.text
        except:
            return tweet.text
    return tweet.text

# ============================================================
# MENGAMBIL MENTION
# ============================================================

def fetch_new_mentions():
    print(timestamp() + Fore.BLUE + "Memeriksa mention baru...")
    mentions = client.get_users_mentions(
        id=client.get_me().data.id,
        tweet_fields=["text", "referenced_tweets"]
    )

    if not mentions.data:
        print(timestamp() + Fore.LIGHTBLACK_EX + "Tidak ada mention baru.")
        return

    for mention in mentions.data:
        if mention.id in processed_ids:
            continue

        print(timestamp() + Fore.MAGENTA + f"Menerima mention dari ID {mention.id}")
        processed_ids.add(mention.id)

        original_text = fetch_parent_text(mention)
        styled = stylize_text(original_text)

        queue.append({
            "reply_to": mention.id,
            "username": mention.author_id,
            "text": styled
        })

        print(timestamp() + Fore.GREEN + "→ Mention diproses dan dimasukkan ke antrean.")

# ============================================================
# MEMPROSES ANTREAN
# ============================================================

def process_queue():
    if not queue:
        print(timestamp() + Fore.LIGHTBLACK_EX + "Antrean kosong. Tidak ada balasan.")
        return

    task = queue.pop(0)
    print(timestamp() + Fore.CYAN + "Mengirim balasan...")

    try:
        client.create_tweet(
            text=task["text"],
            in_reply_to_tweet_id=task["reply_to"]
        )
        print(timestamp() + Fore.GREEN + "Balasan berhasil dikirim.")
    except Exception as e:
        print(timestamp() + Fore.RED + "Gagal mengirim balasan:")
        print(Fore.RED + str(e))

# ============================================================
# LOOP UTAMA
# ============================================================

print(Fore.CYAN + "[SYSTEM] Bot siap dijalankan.\n")

while True:
    try:
        fetch_new_mentions()
        process_queue()
    except Exception as err:
        print(timestamp() + Fore.RED + "Terjadi kesalahan tidak terduga:")
        print(Fore.RED + str(err))

    print(timestamp() + Fore.LIGHTBLACK_EX + f"Menunggu {DELAY_MENIT} menit...")
    time.sleep(CHECK_INTERVAL)
