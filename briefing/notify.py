"""Send a long markdown message to Discord and/or Telegram. Standard library only.

Secrets (GitHub repo -> Settings -> Secrets and variables -> Actions), any combination:
  DISCORD_WEBHOOK_URL                  Discord: Server settings -> Integrations -> Webhooks -> New -> Copy URL
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID Telegram: @BotFather /newbot -> token; message the bot, then
                                       https://api.telegram.org/bot<TOKEN>/getUpdates -> chat.id
WhatsApp isn't supported: it needs a paid Meta Business / Twilio account.
"""
import json, os, time, urllib.request


def chunks(text, limit):
    out, cur = [], ""
    for line in text.splitlines(keepends=True):
        while len(line) > limit:  # very long single line
            out.append(cur); cur = ""; out.append(line[:limit]); line = line[limit:]
        if len(cur) + len(line) > limit:
            out.append(cur); cur = ""
        cur += line
    if cur.strip(): out.append(cur)
    return [c for c in out if c.strip()]


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "signal-lab-briefing"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status


def send_discord(text, url):
    for c in chunks(text, 1900):  # Discord limit is 2000 chars per message
        post(url, {"content": c, "flags": 4})  # 4 = suppress link embeds
        time.sleep(1)


def send_telegram(text, token, chat_id):
    plain = text.replace("**", "")  # plain text: no Markdown escaping problems
    for c in chunks(plain, 4000):  # Telegram limit is 4096
        post(f"https://api.telegram.org/bot{token}/sendMessage",
             {"chat_id": chat_id, "text": c, "disable_web_page_preview": True})
        time.sleep(1)


def send(text):
    sent = []
    if os.getenv("DISCORD_WEBHOOK_URL"):
        try: send_discord(text, os.environ["DISCORD_WEBHOOK_URL"]); sent.append("discord")
        except Exception as e: print("discord failed:", e)
    if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        try: send_telegram(text, os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"]); sent.append("telegram")
        except Exception as e: print("telegram failed:", e)
    return sent
