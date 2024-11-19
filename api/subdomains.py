
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import PlainTextResponse
from database.db import *
from typing import Optional
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


@router.get("/api/subdomains", tags=["Subdomains"])
async def subdomains(
    program: Optional[str] = Query(None),
    scope: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    fresh: Optional[bool] = Query(False),
    count: Optional[bool] = Query(False),
    limit: Optional[int] = Query(1000),
    page: Optional[int] = Query(1),
    json: Optional[bool] = Query(False),
):
    # Fetch the subdomains based on the provided filters
    subdomains = get_subdomains(
        program=program,
        scope=scope,
        provider=provider,
        fresh=fresh,
        count=count,
        limit=limit,
        page=page,
    )

    # If the count flag is set, return the count instead of the subdomains
    if count:
        return {"count": subdomains}

    # If no subdomains are found, raise a 404 error
    if not subdomains:
        raise HTTPException(status_code=404, detail="No subdomains found")

    # Return the response in JSON format if requested
    if json:
        result = [obj.json() for obj in subdomains]
        return result

    # Otherwise, return the response as plain text
    response = "\n".join([f"{obj.subdomain}" for obj in subdomains])
    return PlainTextResponse(response)

@router.get("/api/subdomains/details/{subdomain}", tags=["Subdomains"])
def get_subdomain_detail(subdomain: str):

    subdomain_obj = Subdomains.objects(subdomain=subdomain).first()
    
    if subdomain_obj:
        return subdomain_obj.json()

    raise HTTPException(status_code=404, detail=f"Not found")
