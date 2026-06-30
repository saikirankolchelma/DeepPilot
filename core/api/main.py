import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import workflow_routes, memory_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DeepPilot AI System API", description="API for autonomous engineering multi-agent system.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflow_routes.router, prefix="/api/workflow", tags=["Workflow"])
app.include_router(memory_routes.router, prefix="/api/memory", tags=["Memory"])

UI_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")
if os.path.exists(UI_DIR):
    app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")

@app.get("/")
def serve_ui():
    index_path = os.path.join(UI_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "DeepPilot API Server Running"}

@app.get("/style.css")
def serve_css():
    return FileResponse(os.path.join(UI_DIR, "style.css"))

@app.get("/app.js")
def serve_js():
    return FileResponse(os.path.join(UI_DIR, "app.js"))
