#!/usr/bin/env python3
import sys, re, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import *
from utils import util

def gau(domain):
    command = f"gau {domain} --threads 10 --subs | unfurl domain | sort -u"
    util.logger.debug(f"{util.colors.GRAY}Executing commands: {command}{util.colors.RESET}")
    res = util.run_command_in_zsh(command)
    res_num = len(res) if res else 0
    util.logger.debug(f"{util.colors.GRAY}done for {domain}, results: {res_num}{util.colors.RESET}")
    return res

def gau_domain(domain):
    
    program = Programs.objects(scopes=domain).first()

    if program:
        util.logger.info(f"[{util.current_time()}] running gau module for '{domain}'")
        subs = gau(domain)
        for sub in subs:
            if re.search(r"\.\s*" + re.escape(domain), sub, re.IGNORECASE):
                upsert_subdomain(program.program_name, sub, "gau")
    else:
        util.logger.info(f"[{util.current_time()}] scope for '{domain}' does not exist in watchtower")

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else False

    if not domain:
        util.logger.info(f"Usage: watch_gau domain")
        sys.exit()

    gau_domain(domain)