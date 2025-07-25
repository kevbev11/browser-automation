import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from typing import Dict, Any, List, Optional, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from config.settings import settings
from tools.real_browser_tools import (
    navigate_to_url, take_screenshot, smart_click, smart_fill, 
    get_page_elements, close_browser
)
import json
from typing_extensions import TypedDict

class BrowserAgentState(TypedDict):
    """Enhanced state with browser session tracking"""
    messages: Annotated[list, add_messages]
    browser_session_id: Optional[str]
    current_url: Optional[str]
    task_context: Dict[str, Any]
    completed_actions: List[str]

class RealBrowserAutomationAgent:
    """LangGraph-powered browser automation agent using Smart Tools"""
    
    def __init__(self):
        print("🤖 Initializing Smart Browser Automation Agent...")
        self.setup_tools()
        self.setup_model()
        self.setup_graph()
        print("✅ Smart Browser Automation Agent initialized!")
    
    def setup_tools(self):
        """Define smart browser automation tools"""
        self.tools = [
            navigate_to_url,
            take_screenshot,
            smart_click,
            smart_fill,
            get_page_elements,
            close_browser
        ]
        self.tool_node = ToolNode(self.tools)
        print(f"🔧 Loaded {len(self.tools)} smart browser tools")
    
    def setup_model(self):
        """Setup the model with tools bound"""
        base_model = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.model_temperature,
            api_key=settings.openai_api_key
        )
        self.model = base_model.bind_tools(self.tools)
        print("🔧 Model configured with smart browser tools")
    
    def setup_graph(self):
        """Create LangGraph workflow"""
        workflow = StateGraph(BrowserAgentState)
        
        # Add nodes
        workflow.add_node("agent", self.agent_node)
        workflow.add_node("tools", self.tool_node)
        
        # Define edges
        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "tools": "tools",
                "end": "__end__"
            }
        )
        workflow.add_edge("tools", "agent")
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add memory persistence
        memory = MemorySaver()
        self.app = workflow.compile(checkpointer=memory)
        print("📊 LangGraph workflow configured")
    
    async def agent_node(self, state: BrowserAgentState):
        """Main agent reasoning node"""
        system_prompt = """You are a smart browser automation agent that can understand and interact with web pages intelligently.

Available tools:
- navigate_to_url: Navigate to any website
- take_screenshot: Capture what's currently on screen
- smart_click: Click on elements by describing them (e.g., "search button", "login link", "submit button")
- smart_fill: Fill input fields by describing them (e.g., "search box", "email field", "name field")
- get_page_elements: Analyze the page to see what elements are available to interact with
- close_browser: Close the browser when done

IMPORTANT INSTRUCTIONS:
1. You can click on things by describing what they are - just say "click the search button" or "click the login link"
2. You can fill fields by describing them - just say "fill the search box with 'hello'" or "fill the email field with 'test@example.com'"
3. If you're not sure what's on the page, use get_page_elements to see what's available
4. Always take screenshots to show progress
5. Be conversational and natural - you don't need exact CSS selectors

Current session: {session_id}
Current URL: {current_url}

Break down tasks naturally and accomplish them step by step.
"""
        
        messages = [
            SystemMessage(content=system_prompt.format(
                session_id=state.get("browser_session_id", "default"),
                current_url=state.get("current_url", "None")
            ))
        ] + state["messages"]
        
        response = await self.model.ainvoke(messages)
        
        return {"messages": [response]}
    
    def should_continue(self, state: BrowserAgentState):
        """Determine if we should continue with tools or end"""
        last_message = state["messages"][-1]
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            print(f"🔧 Agent is calling {len(last_message.tool_calls)} tools")
            return "tools"
        
        print("🏁 No more tool calls - ending workflow")
        return "end"
    
    async def run_task(self, task: str, session_id: str = None):
        """Execute a browser automation task"""
        print(f"🎯 Running smart browser task: {task}")
        
        config = {
            "configurable": {
                "thread_id": session_id or "default_thread"
            }
        }
        
        initial_state = {
            "messages": [HumanMessage(content=task)],
            "browser_session_id": session_id or "default",
            "current_url": None,
            "task_context": {"task": task},
            "completed_actions": []
        }
        
        result = await self.app.ainvoke(initial_state, config)
        return result
    
    async def cleanup(self, session_id: str = None):
        """Clean up browser sessions"""
        from tools.real_browser_tools import close_browser_session
        await close_browser_session(session_id or "default")
