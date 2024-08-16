
import tldextract, requests
from config import config
from datetime import datetime


def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_domain_name(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"

def send_discord_message(message):
    data = {
        "content": message
    }

    response = requests.post(config().get('WEBHOOK_URL'), json=data)

    if response.status_code == 204:
        pass
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
