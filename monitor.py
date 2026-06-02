import os
import socket
import urllib.request
import urllib.parse
import json
import ssl

# Конфигурация из переменных окружения (секретов GitHub) 
SERVER_IP = os.environ["SERVER_IP"]
SERVER_PORT = int(os.environ["SERVER_PORT"])
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
TIMEOUT = int(os.environ.get("TIMEOUT", "10"))

def check_ssh():
    """Проверяет SSH-баннер сервера."""
    try:
        with socket.create_connection((SERVER_IP, SERVER_PORT), timeout=TIMEOUT) as s:
            # Читаем SSH-баннер
            banner = b""
            while b"\n" not in banner and len(banner) < 256:
                chunk = s.recv(1)
                if not chunk:
                    break
                banner += chunk
            banner_str = banner.decode("ascii", errors="ignore").strip()
            return banner_str.startswith("SSH-"), banner_str
    except Exception as e:
        return False, str(e)

def send_telegram(message):
    """Отправляет сообщение в Telegram."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true"
    }).encode()
    
    ctx = ssl.create_default_context()
    
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
        result = json.loads(response.read())
        return result.get("ok", False)

def main():
    ok, info = check_ssh()
    
    if ok:
        print(f"✅ SSH работает. Баннер: {info}")
        # Тихий режим - не спамим при успехе
    else:
        print(f"❌ SSH не работает! Причина: {info}")
        msg = (
            f" *СЕРВЕР УПАЛ!*\\n\\n"
            f" IP: `{SERVER_IP}`\\n"
            f"🔌 Порт: `{SERVER_PORT}`\\n"
            f"⏰ Время: мониторинг зафиксировал ошибку\\n"
            f"🔍 Причина: `{info}`"
        )
        sent = send_telegram(msg)
        print(f"Уведомление отправлено: {sent}")
        exit(1)

if __name__ == "__main__":
    main()
