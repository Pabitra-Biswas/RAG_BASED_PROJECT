# from fastapi import FastAPI
# from app.api.routes import router

# app = FastAPI()
# app.include_router(router)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api.routes import router

app = FastAPI()

# Create a templates object pointing to the 'templates' directory
templates = Jinja2Templates(directory="templates")

# Include your API routes from routes.py
app.include_router(router)

# Create a new route for the root URL ("/") that serves the HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # The render function takes the request and the template filename
    return templates.TemplateResponse("index.html", {"request": request})