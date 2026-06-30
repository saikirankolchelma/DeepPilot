from fastapi import FastAPI
from api.routes import workflow_routes, memory_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Deep-Agent AI System API", description="API for autonomous engineering multi-agent system.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflow_routes.router, prefix="/api/workflow", tags=["Workflow"])
app.include_router(memory_routes.router, prefix="/api/memory", tags=["Memory"])

@app.get("/")
def read_root():
    return {"message": "Deep-Agent AI System is running"}
