#!/usr/bin/env python3
import sys, os, re, requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import *
from utils import util

def abuseipdb(domain):
    command = (
        f'curl -s "https://www.abuseipdb.com/whois/{domain}" '
        '-H "user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36" '
        '-b "abuseipdb_session=YOUR-SESSION" | '
        "grep --color=auto --exclude-dir={.bzr,CVS,.git,.hg,.svn,.idea,.tox} "
        "--color=auto --exclude-dir={.bzr,CVS,.git,.hg,.svn,.idea,.tox} "
        "--color=auto --exclude-dir={.bzr,CVS,.git,.hg,.svn,.idea,.tox} "
        f'-E "<li>\\w.*</li>" | sed -E "s/<\\/?li>//g" | sed "s|$|.{domain}|"'
    )

    util.logger.debug(f"{util.colors.GRAY}Executing commands: {command}{util.colors.RESET}")
    res = util.run_command_in_zsh(command)

    res_num = len(res) if res else 0
    util.logger.debug(f"{util.colors.GRAY}done for {domain}, results: {res_num}{util.colors.RESET}")

    return res


def abuseipdb_domain(domain):
    
    program = Programs.objects(scopes=domain).first()

    if program:
        util.logger.info(f"[{util.current_time()}] running abuseipdb module for '{domain}'")
        subs = abuseipdb(domain)

        # save in watch database
        for sub in subs:
            if re.search(r'\.\s*' + re.escape(domain), sub, re.IGNORECASE):
                upsert_subdomain(program.program_name, sub, 'abuseipdb')

    else:
        util.logger.info(f"[{util.current_time()}] scope for '{domain}' does not exist in watch-tower")

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else False

    if domain is False:
        util.logger.info(f"Usage: watch_abuseipdb domain")
        sys.exit()

    abuseipdb_domain(domain)