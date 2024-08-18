#!/usr/bin/env python3
import sys, os, tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

from database.db import *
from utils import util

def nuclei(urls):

    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        for url in urls:
            temp_file.write(f"{url}\n")
    
    urls_file = temp_file.name

    for url in urls:
        command = f"nuclei -l {urls_file} -config {config().get('WATCH_DIR')}/nuclei/public-config.yaml"

        print(f"{util.colors.GRAY}Executing commands: {command}{util.colors.RESET}")
    
        results = util.run_command_in_zsh(command)
        if os.path.exists(urls_file):
            os.remove(urls_file)

        if results != '':
            util.send_discord_message(results, config().get('WEBHOOK_URL_NUCLEI'))

    return True

def nuclei_all():
    
    https_obj = Http.objects().all()

    if https_obj:
        print(f"[{util.current_time()}] running Nuclei module for all HTTP services")
        
        nuclei([http_obj.url for http_obj in https_obj])

if __name__ == "__main__":
    nuclei_all()    