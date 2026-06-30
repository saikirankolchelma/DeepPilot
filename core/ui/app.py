import streamlit as st
import requests
import time

st.set_page_config(page_title="Deep-Agent AI Workspace", layout="wide")
st.title("Deep-Agent AI Workspace")

API_BASE = "http://127.0.0.1:8000/api"

if "task_id" not in st.session_state:
    st.session_state.task_id = None

user_goal = st.text_area("Enter your engineering task:", placeholder="e.g. Build a FastAPI CRUD API for a bookstore")

if st.button("Start Task"):
    if user_goal:
        response = requests.post(f"{API_BASE}/workflow/start", json={"goal": user_goal})
        if response.status_code == 200:
            st.session_state.task_id = response.json()["task_id"]
            st.success(f"Task started! ID: {st.session_state.task_id}")
        else:
            st.error("Failed to start task")

if st.session_state.task_id:
    st.subheader("Task Status")
    status_placeholder = st.empty()
    
    # Polling loop
    timeout = False
    for _ in range(300): # 15 minutes
        try:
            res = requests.get(f"{API_BASE}/workflow/{st.session_state.task_id}/status")
            if res.status_code == 200:
                data = res.json()
                status = data.get("status")
                status_placeholder.info(f"Current Status: {status}")
                
                if status == "completed":
                    final_state = data.get("result", {})
                    st.success("Task Completed!")
                    
                    if "plan" in final_state:
                        with st.expander("Execution Plan"):
                            st.json(final_state["plan"])
                            
                    if "generated_code" in final_state:
                        st.subheader("Generated Code")
                        st.code(final_state.get("generated_code", ""), language="python")
                    
                    if "reflection" in final_state:
                        with st.expander("Agent Reflection & Critique"):
                            st.json(final_state["reflection"])
                    break
                elif status == "failed":
                    st.error(f"Task Failed: {data.get('error')}")
                    break
        except Exception as e:
            st.error(f"Connection error: {e}")
            break
            
        time.sleep(3)
    else:
        st.error("Frontend polling timed out after 15 minutes. The task may still be running in the background.")
