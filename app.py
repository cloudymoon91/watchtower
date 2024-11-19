from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from api.lives import router as lives_router
from api.programs import router as programs_router
from api.subdomains import router as subdomains_router
from api.http import router as http_router

from operation_all import main_loop


app = FastAPI()

app.include_router(lives_router)
app.include_router(programs_router)
app.include_router(subdomains_router)
app.include_router(http_router)

# Mount static directory for serving CSS, JS, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")
# Set up templates directory for Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Define the endpoints
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == '__main__':
    main_loop()
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
        

