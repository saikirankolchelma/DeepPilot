from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from workflows.state_schema import AgentState
from workflows.nodes import (
    plan_node, research_node, code_node, 
    test_node, debug_node, reflect_node
)
from workflows.edges import route_after_test, route_after_reflect

def build_workflow():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", plan_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("coder", code_node)
    workflow.add_node("tester", test_node)
    workflow.add_node("debugger", debug_node)
    workflow.add_node("reflector", reflect_node)

    # Set entry point
    workflow.set_entry_point("planner")

    # Add edges
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "coder")
    workflow.add_edge("coder", "tester")
    
    # Conditional edge after testing
    workflow.add_conditional_edges(
        "tester",
        route_after_test,
        {
            "debug": "debugger",
            "reflect": "reflector"
        }
    )
    
    # Debugger loops back to tester
    workflow.add_edge("debugger", "tester")
    
    # Conditional edge after reflection
    workflow.add_conditional_edges(
        "reflector",
        route_after_reflect,
        {
            "end": END,
            "code": "coder"
        }
    )

    # Compile the graph with a checkpointer for state persistence
    memory_saver = MemorySaver()
    app = workflow.compile(checkpointer=memory_saver)
    return app
