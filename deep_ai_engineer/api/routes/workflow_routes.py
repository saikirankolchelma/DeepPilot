from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from workflows.main_graph import build_workflow
import uuid

router = APIRouter()
app_graph = build_workflow()

# In-memory store for active tasks (for production, use Redis)
active_tasks = {}

class TaskRequest(BaseModel):
    goal: str

def run_workflow_task(task_id: str, goal: str):
    initial_state = {
        "task_id": task_id,
        "user_goal": goal,
        "current_step": 0,
        "history": []
    }
    try:
        config = {"configurable": {"thread_id": task_id}}
        final_state = app_graph.invoke(initial_state, config=config)
        active_tasks[task_id] = {"status": "completed", "result": final_state}
    except Exception as e:
        active_tasks[task_id] = {"status": "failed", "error": str(e)}

@router.post("/start")
async def start_task(request: TaskRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {"status": "running"}
    
    # Run graph asynchronously
    background_tasks.add_task(run_workflow_task, task_id, request.goal)
    
    return {"task_id": task_id, "status": "started"}

@router.get("/{task_id}/status")
async def get_task_status(task_id: str):
    task = active_tasks.get(task_id)
    if not task:
        return {"error": "Task not found"}
    return task
