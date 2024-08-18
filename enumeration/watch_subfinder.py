#!/usr/bin/env python3
import sys, os, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import *
from utils import util

def subfinder(domain):

    command = f"subfinder -d {domain} -all"
    print(f"{util.colors.GRAY}Executing commands: {command}{util.colors.RESET}")
    res = util.run_command_in_zsh(command)

    res_num = len(res) if res else 0
    print(f"{util.colors.GRAY}done for {domain}, results: {res_num}{util.colors.RESET}")

    return res

def subfinder_domain(domain):
    
    program = Programs.objects(scopes=domain).first()

    if program:
        print(f"[{util.current_time()}] running Subfinder module for '{domain}'")
        subs = subfinder(domain)
        # todo: save in file

        # save in watchtower database
        if subs:
            for sub in subs:
                if re.search(r'\.\s*' + re.escape(domain), sub, re.IGNORECASE):
                    upsert_subdomain(program.program_name, sub, 'subfinder')
    else:
        print(f"[{util.current_time()}] scope for '{domain}' does not exist in watchtower")
            

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else False

    if domain is False:
        print(f"Usage: watch_subfinder domain")
        sys.exit()

    subfinder_domain(domain)
