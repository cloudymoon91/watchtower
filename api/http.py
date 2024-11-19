from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import PlainTextResponse
from database.db import *
from typing import Optional
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

@router.get('/api/http/tech/{tech_name}', tags=["HTTP"])
async def tech_http(tech_name: str):
    https_obj = Http.objects(tech__icontains=tech_name)

    res_array = [f"{http_obj.url}" for http_obj in https_obj]

    return res_array

@router.get('/api/http/title/{title_name}', tags=["HTTP"])
async def tech_http(title_name: str):
    https_obj = Http.objects(title__icontains=title_name)

    res_array = [f"{http_obj.url}" for http_obj in https_obj]

    return res_array

@router.get("/api/subdomains/http", tags=["HTTP"])
async def http_services(
    program: Optional[str] = Query(None),
    scope: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tech: Optional[str] = Query(None),
    fresh: Optional[bool] = Query(False),
    latest: Optional[bool] = Query(False),
    count: Optional[bool] = Query(False),
    limit: Optional[int] = Query(1000),
    page: Optional[int] = Query(1),
    json: Optional[bool] = Query(False),
):
    # Fetch the subdomains based on the provided filters
    http = get_http_services(
        program=program,
        scope=scope,
        provider=provider,
        title=title,
        status=status,
        tech=tech,
        fresh=fresh,
        latest=latest,
        count=count,
        limit=limit,
        page=page,
    )

    # If the
    if count:
        return {"count": http}

    # If no http are found, raise a 404 error
    if not http:
        raise HTTPException(status_code=404, detail="No HTTP service found")

    # Return the response in JSON format if requested
    if json:
        result = [obj.json() for obj in http]
        return result

    # Otherwise, return the response as plain text
    response = "\n".join([f"{obj.subdomain}" for obj in http])
    return PlainTextResponse(response)


@router.get("/api/subdomains/http/details/{subdomain}", tags=["HTTP"])
def get_http_service_detail(subdomain: str):

    http_obj = Http.objects(subdomain=subdomain).first()

    if http_obj:
        return http_obj.json()

    raise HTTPException(
        status_code=404, detail=f"Did not found an HTTP service for {subdomain}"
    )


@router.get("/api/technologies", tags=["Technologies"])
async def get_technologies():
    techs = Http.objects.distinct("tech")
    response = "\n".join([f"{obj}" for obj in techs])
    return PlainTextResponse(response)