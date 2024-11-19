#!/usr/bin/env python3
import sys, re, os, tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import *
from utils import util

def dynamic_brute(domain):
    # Paths for temporary files
    with tempfile.TemporaryDirectory() as temp_dir:
        dns_brute = os.path.join(temp_dir, f"{domain}.dns_brute")
        dns_gen_words = os.path.join(temp_dir, "dnsgen-words.tx")
        alt_dns_words = os.path.join(temp_dir, "altdns-words.txt")
        merged_path = os.path.join(temp_dir, "words-merged.tx")
        domain_dns_gen = os.path.join(temp_dir, f"{domain}.dns_gen")

        # Step 1: Prepare wordlist for dynamic brute
        commands = [
            f"curl -s https://raw.githubusercontent.com/AlephNullSK/dnsgen/master/dnsgen/words.txt -o {dns_gen_words}",
            f"curl -s https://raw.githubusercontent.com/infosec-au/altdns/master/words.txt -o {alt_dns_words}",
            f"cat {dns_gen_words} {alt_dns_words} | sort -u > {merged_path}",
        ]
        for cmd in commands:
            util.logger.debug(f"{util.colors.GRAY}Executing command: {cmd}{util.colors.RESET}")
            util.run_command_in_zsh(cmd)

        # Step 2: Get subdomains for dynamic brute
        subdomains = Subdomains.objects(scope=domain)
        with open(dns_brute, "w") as file:
            file.write("\n".join([f"{sub.subdomain}" for sub in subdomains]))

        command = f"cat {dns_brute} | dnsgen -w {merged_path} - | tee {domain_dns_gen}"
        dns_gen_result = util.run_command_in_zsh(command)

        if len(dns_gen_result) > 30000000:
            subdomains = LiveSubdomains.objects(scope=domain)
            with open(dns_brute, "w") as file:
                file.write("\n".join([f"{sub.subdomain}" for sub in subdomains]))
                util.run_command_in_zsh(command)

        # Step 3: Run shuffledns
        shuffledns_command = (
            f"shuffledns -list {domain_dns_gen} -d {domain} -r ~/.resolvers "
            f"-m $(which massdns) -mode resolve -t 100 -silent"
        )
        util.logger.debug(f"{util.colors.GRAY}Executing command: {shuffledns_command}{util.colors.RESET}")
        result = util.run_command_in_zsh(shuffledns_command)

        return result

def ns_dynamic_brute_domain(domain):
    
    program = Programs.objects(scopes=domain).first()

    if program:
        util.logger.info(f"[{util.current_time()}] running ns_brute module for '{domain}'")
        subs = dynamic_brute(domain)
        for sub in subs:
            if re.search(r"\.\s*" + re.escape(domain), sub, re.IGNORECASE):
                upsert_subdomain(program.program_name, sub, "dynamic_brute")
                upsert_lives(domain=domain, subdomain=sub, ips=[], tag="")
    else:
        util.logger.info(f"[{util.current_time()}] scope for '{domain}' does not exist in watchtower")

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else False

    if not domain:
        util.logger.info(f"Usage: watch_ns_brute domain")
        sys.exit()

    ns_dynamic_brute_domain(domain)