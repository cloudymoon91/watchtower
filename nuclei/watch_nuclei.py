#!/usr/bin/env python3
import sys, os, tempfile
from database.db import *
from config import config
from utils import util

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
def nuclei(urls):

    
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
        for url in urls:
            temp_file.write(f"{url}\n")

    urls_file = temp_file.name

    command = f"nuclei -l {urls_file} -config {config().get('WATCH_DIR')}/nuclei/public-config.yaml"

    util.logger.info(f"{util.colors.GRAY}Executing commands: {command}{util.colors.RESET}")

    results = util.run_command_in_zsh(command, read_line=False)

    if os.path.exists(urls_file):
        os.remove(urls_file)

    return results

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else False

    if domain is False:
        util.logger.info(f"Usage: watch_http domain")
        sys.exit()

    https_obj = get_http_services(scope=domain)
    
    if https_obj:
        util.logger.info(f"[{util.current_time()}] running Nuclei module for all HTTP services")

        results = nuclei([http_obj.url for http_obj in https_obj])

        if results != "":
            util.send_discord_file(results, "WEBHOOK_URL_NUCLEI")
