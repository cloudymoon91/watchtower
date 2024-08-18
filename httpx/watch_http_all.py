#!/usr/bin/env python3
import sys, os, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import util
from database.db import *

def httpx(subdomains_array, domain):

    for subdomain in subdomains_array:
        command = f"echo {subdomain} | httpx -silent -json -favicon -fhr -tech-detect -irh -include-chain -timeout 3 -retries 1 -threads 5 -rate-limit 4 -ports 443 -extract-fqdn -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0' -H 'Referer: https://{subdomain}'"

        print(f"{util.colors.GRAY}Executing commands: {command}{util.colors.RESET}")
        
        results = util.run_command_in_zsh(command, read_line=False)

        if results != '':
            json_obj = json.loads(results)
            upsert_http({
                "subdomain": subdomain,
                "scope": domain,
                "ips": json_obj.get('a', ''),
                "tech": json_obj.get('tech', []),
                "title": json_obj.get('title', ''),
                "status_code": json_obj.get('status_code', ''),
                "headers": json_obj.get('header', {}),
                "url": json_obj.get('url', ''),
                "final_url": json_obj.get('final_url', ''),
                "favicon": json_obj.get('favicon', '')
            })

    return True

def httpx_all():
    
    programs = Programs.objects().all()

    for program in programs:
        for scope in program.scopes:
            domain = scope
            obj_lives = LiveSubdomains.objects(scope=domain)

            if obj_lives:
                print(f"[{util.current_time()}] running HTTPx module for '{domain}'")
                
                httpx([obj_live.subdomain for obj_live in obj_lives], domain)

            else:
                print(f"[{util.current_time()}] domain '{domain}' does not exist in watchtower")

if __name__ == "__main__":
    httpx_all()