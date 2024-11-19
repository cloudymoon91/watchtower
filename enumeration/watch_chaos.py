#!/usr/bin/env python3
import sys, re, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import *

from config import config
from utils import util

CHAOS_FOLDER = os.path.join(config().get('WATCH_DIR'), "chaos")

def chaos(domain):
    file_path = os.path.join(CHAOS_FOLDER, f"{domain}.txt")

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            lines = [line.strip() for line in file.readlines()]
        return lines
    else:
        util.logger.info(f"{domain} does not exist in Chaos module.")
        return []

def chaos_domain(domain):
    
    program = Programs.objects(scopes=domain).first()

    if program:
        util.logger.info(f"[{util.current_time()}] running Chaos module for '{domain}'")
        subs = chaos(domain)
        for sub in subs:
            if (
                re.search(r"\.\s*" + re.escape(domain), sub, re.IGNORECASE)
                and "*" not in sub
            ):
                upsert_subdomain(program.program_name, sub, "chaos")
    else:
        util.logger.info(f"[{util.current_time()}] scope for '{domain}' does not exist in watchtower")

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else False

    if not domain:
        util.logger.info(f"Usage: watch_chaos domain")
        sys.exit()

    chaos_domain(domain)