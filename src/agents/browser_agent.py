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
from tools.browser_tools import (
    navigate_to_url, take_screenshot, click_element, 
    fill_input, get_page_content, wait_for_element
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

class BrowserAutomationAgent:
    """LangGraph-powered browser automation agent using AgentCore"""
    
    def __init__(self):
        print("🤖 Initializing Browser Automation Agent...")
        self.setup_tools()
        self.setup_model()
        self.setup_graph()
        print("✅ Browser Automation Agent initialized!")
    
    def setup_tools(self):
        """Define browser automation tools"""
        self.tools = [
            navigate_to_url,
            take_screenshot,
            click_element,
            fill_input,
            get_page_content,
            wait_for_element
        ]
        self.tool_node = ToolNode(self.tools)
        print(f"🔧 Loaded {len(self.tools)} browser tools")
    
    def setup_model(self):
        """Setup the model with tools bound"""
        base_model = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.model_temperature,
            api_key=settings.openai_api_key
        )
        # Bind tools to the model so it can call them
        self.model = base_model.bind_tools(self.tools)
        print("🔧 Model configured with tools")
    
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
        system_prompt = """You are a browser automation agent. Your job is to use the available tools to complete browser automation tasks.

Available tools:
- navigate_to_url: Navigate to a specific URL
- take_screenshot: Take a screenshot of the current page
- click_element: Click on an element using CSS selector
- fill_input: Fill an input field with text
- get_page_content: Get text content from page
- wait_for_element: Wait for an element to appear

IMPORTANT: You must use the tools to actually perform actions. Don't just describe what you would do - actually call the tools!

Current session: {session_id}
Current URL: {current_url}
Completed actions: {completed_actions}

For the current task, break it down into steps and use the appropriate tools for each step.
"""
        
        messages = [
            SystemMessage(content=system_prompt.format(
                session_id=state.get("browser_session_id", "default"),
                current_url=state.get("current_url", "None"),
                completed_actions=state.get("completed_actions", [])
            ))
        ] + state["messages"]
        
        response = await self.model.ainvoke(messages)
        
        return {"messages": [response]}
    
    def should_continue(self, state: BrowserAgentState):
        """Determine if we should continue with tools or end"""
        last_message = state["messages"][-1]
        
        # Check if the last message has tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            print(f"🔧 Agent is calling {len(last_message.tool_calls)} tools")
            return "tools"
        
        print("🏁 No more tool calls - ending workflow")
        return "end"
    
    async def run_task(self, task: str, session_id: str = None):
        """Execute a browser automation task"""
        print(f"🎯 Running task: {task}")
        
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
