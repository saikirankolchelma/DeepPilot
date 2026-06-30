import os
import re
from workflows.state_schema import AgentState
from models.model_router import ModelRouter
from memory.memory_router import MemoryRouter
from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.coding_agent import CodingAgent
from agents.debugging_agent import DebuggingAgent
from agents.testing_agent import TestingAgent
from agents.reflection_agent import ReflectionAgent
from tools.terminal_tool import run_shell_command

# Initialize shared components
router = ModelRouter()
memory = MemoryRouter()

planner = PlannerAgent(router)
researcher = ResearchAgent(router)
coder = CodingAgent(router)
debugger = DebuggingAgent(router)
tester = TestingAgent(router)
reflector = ReflectionAgent(router)

WORKSPACE_DIR = os.path.join(os.getcwd(), "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

def extract_code_block(text: str) -> str:
    """Helper to extract code from markdown block."""
    blocks = re.findall(r'```(?:python)?\n(.*?)\n```', text, re.DOTALL)
    if blocks:
        return blocks[0]
    return text

def plan_node(state: AgentState) -> AgentState:
    print(f"--- PLANNING TASK: {state['user_goal']} ---")
    plan = planner.generate_plan(state['user_goal'])
    state['plan'] = plan
    memory.store_short_term(state['task_id'], "Planning", "Generated execution plan.")
    return state

def research_node(state: AgentState) -> AgentState:
    print("--- RESEARCHING ---")
    topic = state['user_goal']
    context = researcher.research_topic(topic)
    state['research_context'] = context
    memory.store_short_term(state['task_id'], "Research", "Gathered technical context.")
    return state

def code_node(state: AgentState) -> AgentState:
    print("--- CODING ---")
    mem_context = memory.retrieve_relevant_context(state['user_goal'])
    code_str = coder.write_code(
        task_description=state['user_goal'],
        research_context=state.get('research_context', ''),
        memory_context=mem_context if isinstance(mem_context, str) else str(mem_context)
    )
    
    clean_code = extract_code_block(code_str)
    with open(os.path.join(WORKSPACE_DIR, "main.py"), "w", encoding="utf-8") as f:
        f.write(clean_code)
        
    state['generated_code'] = clean_code
    memory.store_short_term(state['task_id'], "Coding", "Generated initial code implementation.")
    return state

def test_node(state: AgentState) -> AgentState:
    print("--- TESTING ---")
    test_str = tester.generate_tests(state.get('generated_code', ''))
    
    clean_test_code = extract_code_block(test_str)
    test_file_path = os.path.join(WORKSPACE_DIR, "test_main.py")
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(clean_test_code)
        
    state['test_code'] = clean_test_code
    
    # Run tests using terminal tool physically
    test_results = run_shell_command.invoke({"command": f"pytest test_main.py", "cwd": WORKSPACE_DIR})
    state['test_results'] = test_results
    
    memory.store_short_term(state['task_id'], "Testing", "Generated and executed tests physically.")
    return state

def debug_node(state: AgentState) -> AgentState:
    print("--- DEBUGGING ---")
    # Pass the test_results instead of error_message
    fixed_code_str = debugger.debug_error(state.get('generated_code', ''), state.get('test_results', ''))
    
    clean_fixed_code = extract_code_block(fixed_code_str)
    with open(os.path.join(WORKSPACE_DIR, "main.py"), "w", encoding="utf-8") as f:
        f.write(clean_fixed_code)
        
    state['generated_code'] = clean_fixed_code
    memory.store_short_term(state['task_id'], "Debugging", "Applied fixes and overwrote main.py.")
    return state

def reflect_node(state: AgentState) -> AgentState:
    print("--- REFLECTING ---")
    eval_result = reflector.evaluate(
        state['user_goal'], 
        state.get('generated_code', ''), 
        state.get('test_results', '')
    )
    state['reflection'] = eval_result
    
    if eval_result.get('is_correct', False):
        memory.store_episodic(state['task_id'], f"Successfully completed: {state['user_goal']}", True)
        
    return state
