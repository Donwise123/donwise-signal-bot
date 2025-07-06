import os
import asyncio
import logging
from datetime import datetime, date
import pytz
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from keep_alive import keep_alive

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load environment variables
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
session_str = os.environ['SESSION_STRING']

# Telegram Client
client = TelegramClient(StringSession(session_str), api_id, api_hash)

# Timezone
tz = pytz.timezone("Africa/Lagos")

# Channels
SOURCE_CHANNELS = [
    'GaryGoldLegacy', 'firepipsignals', 'habbyforex',
    'Goldforexsignalfx11', 'Forex_Top_Premium_Signals',
    'forexgdp0', 'bengoldtrader', 'kojoforextrades'
]
TARGET_CHANNEL = 'DonwiseVault'

# State
daily_signals = set()
last_reset_date = None

def reset_daily_state():
    global daily_signals, last_reset_date
    today = datetime.now(tz).date()
    if last_reset_date != today:
        daily_signals = set()
        last_reset_date = today
        logging.info("🔁 New day. Reset state.")

def is_valid_signal(msg):
    msg_l = msg.lower()
    blocked_keywords = ['invest', 'investment', 'promo', 'bonus', 'reward', 'advert']
    if any(bad in msg_l for bad in blocked_keywords):
        return False
    sl_keywords = ['sl', 'stop loss', 'stoploss']
    tp_keywords = ['tp', 'take profit']
    return any(sl in msg_l for sl in sl_keywords) and any(tp in msg_l for tp in tp_keywords)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    global daily_signals
    reset_daily_state()

    if len(daily_signals) >= 6:
        return
    if event.media:
        return

    msg = event.message.message.strip()
    if not is_valid_signal(msg):
        return
    if msg in daily_signals:
        logging.info("⚠️ Duplicate signal skipped.")
        return

    final_msg = f"{msg}\n\n_By @RealDonwise 🔥 | Donwise Copytrade Vault_"
    await client.send_message(TARGET_CHANNEL, final_msg, parse_mode='markdown')
    daily_signals.add(msg)
    logging.info(f"📩 Forwarded signal: {msg[:50]}...")

async def main():
    await client.start()
    logging.info("🚀 Bot started.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    keep_alive()
    try:
        client.loop.run_until_complete(main())
    except Exception as e:
        logging.error(f"❌ Bot crashed: {e}")
