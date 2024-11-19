
from programs import watch_sync_programs
from name_resolution import watch_ns_all
from enumeration import watch_enum_all
from httpx import watch_http_all
from nuclei import watch_nuclei_all
import time
import threading
from database.db import *
from utils import util
        
def programs_opertion():
    while True:
        watch_sync_programs.scan_programs()
        
        util.logger.info("end round programs_opertion: {}".format(util.index_programs))
        util.index_programs += 1
        time.sleep(8*3600)
        
def enumeration_opertion():
    while True:
        watch_enum_all.enumeration_all()
        
        util.logger.info("end round enumeration_opertion: {}".format(util.index_enumeration))
        util.index_enumeration += 1
        time.sleep(4*3600)
        
def ns_opertion():
    while True:
        watch_ns_all.ns_all()
        
        util.logger.info("end round ns_opertion: {}".format(util.index_ns))
        util.index_ns += 1
        time.sleep(4*3600)
        
def httpx_opertion():
    while True:
        watch_http_all.httpx_all()
        
        util.logger.info("end round httpx_opertion: {}".format(util.index_httpx))
        util.index_httpx += 1
        time.sleep(8*3600) 
        
def nuclei_opertion():
    while True:
        watch_nuclei_all.nuclei_all() 
        
        util.logger.info("end round nuclei_opertion: {}".format(util.index_nuclei))
        util.index_nuclei += 1
        time.sleep(3*3600)
        
   
def main_loop(): 
    util.logger.info("____________________________________________")
    threading.Thread(target=programs_opertion, args=()).start()
    threading.Thread(target=enumeration_opertion, args=()).start()
    threading.Thread(target=ns_opertion, args=()).start()
    threading.Thread(target=httpx_opertion, args=()).start()
    threading.Thread(target=nuclei_opertion, args=()).start()
