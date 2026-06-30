from workflows.state_schema import AgentState

def route_after_test(state: AgentState) -> str:
    """Decide what to do after testing."""
    results = state.get("test_results", "").lower()
    if "fail" in results or "error" in results:
        return "debug"
    return "reflect"

def route_after_reflect(state: AgentState) -> str:
    """Decide if we are done or need another iteration."""
    reflection = state.get("reflection", {})
    is_correct = reflection.get("is_correct", False)
    
    if is_correct:
        return "end"
    return "code" # Send back to coding agent to apply suggestions
