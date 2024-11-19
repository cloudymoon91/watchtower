#!/usr/bin/env python3
import sys, tempfile, json, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import util
from database.db import *
from config import config

def dnsx(subdomains_array, domain):
    # Create a temporary file to store the list of subdomains
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
        for sub in subdomains_array:
            temp_file.write(f"{sub}\n")

    subdomains_file = temp_file.name

    # Define the command to run dnsx with specified parameters
    command = (
        f"dnsx -l {subdomains_file} -silent -wd {domain} -resp -json "
        f"-rl 30 -t 10 -r 8.8.4.4,129.250.35.251,208.67.222.222"
    )

    util.logger.debug(f"{util.colors.GRAY}Executing command: {command}{util.colors.RESET}")

    # Execute the command and capture the results
    results = util.run_command_in_zsh(command)
    
    if os.path.exists(subdomains_file):
        os.remove(subdomains_file)
    # Process the results and upsert live subdomains into the database

    return results

def ns_domain(domain):
    
    # Retrieve subdomains associated with the given domain from the database
    obj_subs = Subdomains.objects(scope=domain)

    if obj_subs:
        util.logger.debug(f"[{util.current_time()}] Running Dnsx module for '{domain}'")

        # Call the dnsx function with the list of subdomains and domain name
        results = dnsx([obj_sub.subdomain for obj_sub in obj_subs], domain)

        for result in results:
            obj = json.loads(result)
            tag = util.get_ip_tag(obj.get("a"))
            upsert_lives(
                domain=domain,
                subdomain=obj.get("host"),
                ips=obj.get("a"),
                tag=tag,
            )
    else:
        util.logger.info(f"[{util.current_time()}] Domain '{domain}' does not exist in watchtower")


if __name__ == "__main__":
    # Get the domain from command-line arguments
    domain = sys.argv[1] if len(sys.argv) > 1 else False

    if not domain:
        util.logger.info("Usage: watch_ns <domain>")
        sys.exit()

    ns_domain(domain)