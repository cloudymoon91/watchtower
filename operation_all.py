
from programs import watch_sync_programs
from name_resolution import watch_ns_all
from enumeration import watch_enum_all
from httpx import watch_http_all
from nuclei import watch_nuclei_all
import time
from database.db import *
from utils import util

def programs_all():
    watch_sync_programs.scan_programs()
            
index = 1
def main_loop():
    while True:
        programs_all()
        watch_enum_all.enumeration_all()
        watch_ns_all.ns_all()
        watch_http_all.httpx_all()
        watch_nuclei_all.nuclei_all() 
        
        print("end round: {}".format(index))
        index += 1
        time.sleep(4*3600)
