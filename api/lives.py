
from fastapi import APIRouter
from database.db import *
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta


router = APIRouter()


# TODO: @app.route('/api/lives/domain/<domain>')
# TODO: @app.route('/api/lives/program/<p_name>')

@router.get('/api/lives/all', tags=["Lives"])
async def all_lives():
    twelve_hours_ago = datetime.now() - timedelta(hours=12)
    lives_obj = LiveSubdomains.objects(last_update__gte=twelve_hours_ago).all()
    
    res_array = [f"{live_obj.subdomain}" for live_obj in lives_obj]
    return res_array

@router.get('/api/lives/fresh', tags=["Lives"])
async def all_lives_fresh():
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

    fresh_lives = LiveSubdomains.objects(created_date__gte=twenty_four_hours_ago)
    
    res_array = [f"{fresh_live.subdomain}" for fresh_live in fresh_lives]
    return res_array

@router.get('/api/lives/provider/{provider}', tags=["Lives"])
async def all_lives_provider(provider: str):
    
    twelve_hours_ago = datetime.now() - timedelta(hours=12)
    subdomains = Subdomains.objects(providers=[provider])
    lives = [
        LiveSubdomains.objects(
            subdomain=sub.subdomain, last_update__gte=twelve_hours_ago
        ).first()
        for sub in subdomains
        if LiveSubdomains.objects(
            subdomain=sub.subdomain, last_update__gte=twelve_hours_ago
        )
    ]
    res_array = [f"{live.subdomain}" for live in lives]
    return res_array

@router.get('/api/live/subdomain/{subdomain}', tags=["Lives"])
async def all_live_single(subdomain: str):
    
    live_obj = LiveSubdomains.objects(subdomain=subdomain).first()
    subdomain_obj = Subdomains.objects(subdomain=subdomain).first()

    if live_obj and subdomain_obj:

        return {
            "program_name": live_obj.program_name,
            "subdomain": live_obj.subdomain,
            "scope": live_obj.scope,
            "ips": live_obj.ips or [],
            "cdn": live_obj.cdn,
            "providers": subdomain_obj.providers or [],
            "created_date": (
                live_obj.created_date.isoformat()
                if live_obj.created_date
                else None
            ),
            "last_update": (
                live_obj.last_update.isoformat()
                if live_obj.last_update
                else None
            ),
        }
    
    return JSONResponse({'error': f"{subdomain} not found"})
