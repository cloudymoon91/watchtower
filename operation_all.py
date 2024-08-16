
from programs import watch_sync_programs
from enumeration import watch_subfinder, watch_crtsh, watch_abuseipdb
from name_resolution import watch_ns_all
import time
from database.db import *
from utils import util



def programs_all():
    watch_sync_programs.scan_programs()

def enumeration_all():
    programs = Programs.objects.all()

    for program in programs:
        print(f"[{util.current_time()}] let's go for '{program.program_name}' program...")
        scopes = program.scopes

        for scope in scopes:
            print(f"[{util.current_time()}] enumerating subdomains for '{scope}' domain...")
            
            watch_subfinder.subfinder_domain(scope)
            watch_crtsh.crtsh_domian(scope)
            watch_abuseipdb.abuseipdb_domain(scope)
            

def main_loop():
    while True:
        programs_all()
        enumeration_all()
        watch_ns_all.ns_all()
        
        time.sleep(3600)
