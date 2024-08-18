#!/usr/bin/env python3
import sys, re, os, tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import *
from utils import util

def static_brute(domain):
    # Paths for temporary files
    with tempfile.TemporaryDirectory() as temp_dir:
        best_dns_path = os.path.join(temp_dir, "best-dns-wordlist.txt")
        subdomains_path = os.path.join(temp_dir, "2m-subdomains.txt")
        crunch_path = os.path.join(temp_dir, "4-lower.txt")
        static_words_path = os.path.join(temp_dir, "static-finals.txt")
        domain_static_path = os.path.join(temp_dir, f"{domain}.static")

        # Step 1: Prepare wordlist for static brute
        commands = [
            f"curl -s https://wordlists-cdn.assetnote.io/data/manual/best-dns-wordlist.txt -o {best_dns_path}",
            f"curl -s https://wordlists-cdn.assetnote.io/data/manual/2m-subdomains.txt -o {subdomains_path}",
            f"crunch 1 4 abcdefghijklmnopqrstuvwxyz1234567890 > {crunch_path}",
            f"cat {best_dns_path} {subdomains_path} {crunch_path} | sort -u > {static_words_path}",
            f"awk -v domain='{domain}' '{{print $0\".\"domain}}' {static_words_path} > {domain_static_path}",
        ]
        for cmd in commands:
            print(f"{util.colors.GRAY}Executing command: {cmd}{util.colors.RESET}")
            util.run_command_in_zsh(cmd)

        # Step 2: Run shuffledns
        shuffledns_command = (
            f"shuffledns -list {domain_static_path} -d {domain} -r ~/.resolvers "
            f"-m $(which massdns) -mode resolve -t 100 -silent"
        )
        print(f"{util.colors.GRAY}Executing command: {shuffledns_command}{util.colors.RESET}")
        result = util.run_command_in_zsh(shuffledns_command)

        return result

def ns_static_brute_domain(domain):

    program = Programs.objects(scopes=domain).first()

    if program:
        print(f"[{util.current_time()}] running ns_brute module for '{domain}'")
        subs = static_brute(domain)
        for sub in subs:
            if re.search(r"\.\s*" + re.escape(domain), sub, re.IGNORECASE):
                upsert_subdomain(program.program_name, sub, "static_brute")
                upsert_lives(domain=domain, subdomain=sub, ips=[], tag="")
    else:
        print(f"[{util.current_time()}] scope for '{domain}' does not exist in watchtower")

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else False

    if not domain:
        print(f"Usage: watch_ns_brute domain")
        sys.exit()

    ns_static_brute_domain(domain)