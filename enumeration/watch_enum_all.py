

from enumeration import watch_subfinder, watch_crtsh, watch_abuseipdb
from enumeration import watch_chaos, watch_wayback, watch_gau
from database.db import *
from utils import util

def enumeration_all():
    programs = Programs.objects.all()

    for program in programs:
        util.logger.info(f"[{util.current_time()}] let's go for '{program.program_name}' program...")
        scopes = program.scopes

        for scope in scopes:
            util.logger.info(f"[{util.current_time()}] enumerating subdomains for '{scope}' domain...")
            
            watch_subfinder.subfinder_domain(scope)
            watch_crtsh.crtsh_domain(scope)
            watch_abuseipdb.abuseipdb_domain(scope)
            watch_chaos.chaos_domain(scope)
            watch_gau.gau_domain(scope)
            watch_wayback.wayback_domain(scope)