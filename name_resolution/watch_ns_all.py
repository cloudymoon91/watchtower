#!/usr/bin/env python3
import os, sys, json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import *

from utils import util
from name_resolution import watch_ns, watch_ns_static_brute, watch_ns_dynamic_brute

def ns_all():
    
    programs = Programs.objects().all()
    for program in programs:
        for domain in program.scopes:
            util.logger.info(f"[{util.current_time()}] name resolution for '{domain}' domain...")

            watch_ns.ns_domain(domain)
            with open('settings.json', 'r') as file:
                settings = json.load(file)

            if settings.get("DO_NS_BRUTE"):
                watch_ns_static_brute.ns_static_brute_domain(domain)
                watch_ns_dynamic_brute.ns_dynamic_brute_domain(domain)

if __name__ == "__main__":
    ns_all()