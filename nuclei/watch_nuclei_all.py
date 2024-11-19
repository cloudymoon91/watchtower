#!/usr/bin/env python3
import sys, os, tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

from database.db import *
from utils import util

def nuclei(urls):

    
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
        for url in urls:
            temp_file.write(f"{url}\n")

    urls_file = temp_file.name

    command = f"nuclei -l {urls_file} -config {config().get('WATCH_DIR')}/nuclei/public-config.yaml"

    util.logger.debug(f"{util.colors.GRAY}Executing commands: {command}{util.colors.RESET}")

    results = util.run_command_in_zsh(command, read_line=False)
    
    if os.path.exists(urls_file):
        os.remove(urls_file)

    return results

def nuclei_all():
    
    https_obj = get_http_services()


    if https_obj:
        util.logger.info(f"[{util.current_time()}] running Nuclei module for all HTTP services")

        http_list = [http_obj.url for http_obj in https_obj]
        chunks = util.split_list_into_chunks(http_list, 50)
        # Print the result
        for idx, chunk in enumerate(chunks):
            util.logger.info("nuclei_all chunk: {} -> {} at round: {} and all is:{} -> {}".format(
                idx, len(chunk), util.index_nuclei, len(chunks), len(http_list)))
            results = nuclei(chunk)
            
            util.logger.debug(results)
            if results != "":
                util.send_discord_file(results, "WEBHOOK_URL_NUCLEI")

if __name__ == "__main__":
    nuclei_all()    