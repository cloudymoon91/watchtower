#!/usr/bin/env python3
import sys, os, json, tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import util
from database.db import *

def httpx(subdomains, domain):

    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
        for sub in subdomains:
            temp_file.write(f"{sub}\n")

    subdomains_file = temp_file.name

    command = f"httpx -l {subdomains_file} -silent -json -favicon -fhr -tech-detect -irh -include-chain -timeout 3 -retries 1 -threads 5 -rate-limit 4 -ports 443 -extract-fqdn -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0' -H 'Referer: https://{domain}'"

    util.logger.debug(f"{util.colors.GRAY}Executing commands: {command}{util.colors.RESET}")

    result = util.run_command_in_zsh(command, read_line=False)
    responses = []
    for r in result.splitlines():
        response = json.loads(r)
        responses.append(response)
    os.remove(subdomains_file)
    return responses

def httpx_domain(domain):
    with open('settings.json', 'r') as file:
        settings = json.load(file)
        
    obj_lives = get_lives(scope=domain, tag= None if settings.get("TAG") == "" else settings.get("TAG"))

    if obj_lives:
        util.logger.info(f"[{util.current_time()}] running HTTPx module for '{domain}'")
        subdomains = [obj.subdomain for obj in obj_lives]
        result = httpx(subdomains, domain)
        for obj in result:
            http = {
                "subdomain": obj.get("input"),
                "scope": domain,
                "ips": obj.get("a", ""),
                "tech": obj.get("tech", []),
                "title": obj.get("title", ""),
                "status_code": obj.get("status_code", ""),
                "headers": obj.get("header", {}),
                "url": obj.get("url", ""),
                "final_url": obj.get("final_url", ""),
                "favicon": obj.get("favicon", ""),
            }
            upsert_http(**http)
    

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else False

    if domain is False:
        util.logger.info(f"Usage: watch_http domain")
        sys.exit()
        
    httpx_domain(domain)


    