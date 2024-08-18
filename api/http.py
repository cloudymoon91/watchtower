from fastapi import APIRouter
from database.db import *
from datetime import datetime, timedelta

router = APIRouter()

@router.get('/api/http/fresh', tags=["HTTP"])
async def all_http_fresh():
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

    fresh_https = Http.objects(created_date__gte=twenty_four_hours_ago)
    
    res_array = [f"{fresh_http.url}" for fresh_http in fresh_https]
    return res_array

@router.get('/api/http/provider/{provider}', tags=["HTTP"])
async def all_http_provider(provider: str):
    
    twelve_hours_ago = datetime.now() - timedelta(hours=12)
    subdomains = Subdomains.objects(providers=[provider])
    sub_urls = [sub.subdomain for sub in subdomains]
    https = Http.objects(subdomain__in=sub_urls, last_update__gte=twelve_hours_ago)
    
    res_array = [obj.url for obj in https if obj]
    return res_array

@router.get('/api/http/all', tags=["HTTP"])
async def all_http():
    twelve_hours_ago = datetime.now() - timedelta(hours=12)
    https_obj = Http.objects(last_update__gte=twelve_hours_ago).all()

    res_array = [f"{http_obj.url}" for http_obj in https_obj]

    return res_array

