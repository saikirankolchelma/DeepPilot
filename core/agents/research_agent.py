from models.model_router import ModelRouter
from tools.doc_search_tool import search_documentation

class ResearchAgent:
    def __init__(self, model_router: ModelRouter):
        self.router = model_router
        
    def research_topic(self, topic: str, context: str = "") -> str:
        # For simplicity, we just trigger the model to generate a research summary
        # Optionally, it could use the search_documentation tool before answering.
        
        # Simulate tool usage
        docs = search_documentation.invoke({"query": topic, "library_name": "general"})
        
        prompt = f"""
        You are a Staff Research Engineer. Investigate the following topic and provide technical details, 
        best practices, and API usage examples to assist the coding agent.
        
        Topic: {topic}
        Context: {context}
        Search Results: {docs}
        
        Provide a concise, highly technical summary with code examples if applicable.
        """
        
        return self.router.route_task(task_type="research", prompt=prompt)
