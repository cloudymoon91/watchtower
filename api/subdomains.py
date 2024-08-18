
from fastapi import APIRouter
from database.db import *
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get('/api/subdomains/domain/{domain}', tags=["Subdomains"])
async def subdomains_of_domain(domain):
    obj_subdomains = Subdomains.objects(scope=domain)

    if obj_subdomains:
        # Convert query result to list of dictionaries
        res_array = [f"{obj_sub.subdomain}" for obj_sub in obj_subdomains]
        return res_array
    else:
        return JSONResponse({'error': 'subdomain not found'})


@router.get('/api/subdomains/program/{p_name}', tags=["Subdomains"])
async def subdomains_of_program(p_name):
    obj_subdomains = Subdomains.objects(program_name=p_name)

    if obj_subdomains:
        res_array = [f"{obj_sub.subdomain}" for obj_sub in obj_subdomains]
        return res_array
    else:
        return JSONResponse({'error': 'subdomain not found'})
    
@router.get('/api/subdomains/all', tags=["Subdomains"])
async def all_subdomains():
    obj_subdomains = Subdomains.objects().all()

    if obj_subdomains:
        res_array = [f"{obj_sub.subdomain}" for obj_sub in obj_subdomains]
        return res_array
