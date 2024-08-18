
from fastapi import APIRouter
from database.db import *

router = APIRouter()

@router.get('/api/programs/all', tags=["Programs"])
async def all_programs():
    programs = Programs.objects().all()

    response = {}
    for program in programs:
        response[program.program_name] = {
            'scopes': program.scopes,
            'ooscopes': program.ooscopes,
            'config': program.config,
            'created_date': program.created_date,
            }

    # Return JSON response
    return response
