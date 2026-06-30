from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    task_id: str
    user_goal: str
    plan: Optional[dict]
    current_step: int
    research_context: str
    generated_code: str
    test_code: str
    test_results: str
    error_message: str
    reflection: Optional[dict]
    history: List[Dict[str, Any]]
