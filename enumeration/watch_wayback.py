#!/usr/bin/env python3
import sys, re, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import *
from utils import util


def wayback(domain):
    command = f"echo {domain} | waybackurls | unfurl domain | sort -u"
    util.logger.info(f"{util.colors.GRAY}Executing commands: {command}{util.colors.RESET}")
    res = util.run_command_in_zsh(command)
    res_num = len(res) if res else 0
    util.logger.info(f"{util.colors.GRAY}done for {domain}, results: {res_num}{util.colors.RESET}")
    return res

def wayback_domain(domain):
    
    program = Programs.objects(scopes=domain).first()

    if program:
        util.logger.info(f"[{util.current_time()}] running Wayback module for '{domain}'")
        subs = wayback(domain)
        for sub in subs:
            if re.search(r"\.\s*" + re.escape(domain), sub, re.IGNORECASE):
                upsert_subdomain(program.program_name, sub, "wayback")
    else:
        util.logger.info(f"[{util.current_time()}] scope for '{domain}' does not exist in watchtower")

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else False

    if not domain:
        util.logger.info(f"Usage: watch_wayback domain")
        sys.exit()

    wayback_domain(domain)