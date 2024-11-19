
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from database.db import *

router = APIRouter()

@router.get("/api/programs/all", tags=["Programs"])
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


@router.delete("/api/programs/{program_name}", tags=["Programs"])
async def delete_program(program_name: str):
    result = Programs.objects(program_name=program_name).delete()

    if result == 0:
        raise HTTPException(
            status_code=404, detail=f"Program '{program_name}' not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
