
from programs import watch_sync_programs
from enumeration import watch_subfinder, watch_crtsh
import time
from database.db import *


def programs_all():
    watch_sync_programs.scan_programs()

def enumeration_all():
    programs = Programs.objects.all()

    for program in programs:
        print(f"[{current_time()}] let's go for '{program.program_name}' program...")
        scopes = program.scopes

        for scope in scopes:
            print(f"[{current_time()}] enumerating subdomains for '{scope}' domain...")
            
            watch_subfinder.subfinder_domain(scope)
            watch_crtsh.crtsh_domian(scope)
            

def main_loop():
    while True:
        programs_all()
        enumeration_all()
        
        time.sleep(3600)
