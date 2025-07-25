from typing import Optional, Dict, Any
from langchain_core.tools import tool
from bedrock_agentcore.tools.browser_client import BrowserClient
import asyncio
import os
from datetime import datetime

# Global client management
_browser_client: Optional[BrowserClient] = None
_browser_sessions: Dict[str, Any] = {}

def get_browser_client(region: str = "us-west-2") -> BrowserClient:
    """Get or create browser client"""
    global _browser_client
    if _browser_client is None:
        _browser_client = BrowserClient(region)
        _browser_client.start()
    return _browser_client

@tool
async def agentcore_navigate(url: str, session_id: Optional[str] = None) -> str:
    """Navigate to a URL using AgentCore Browser"""
    try:
        client = get_browser_client()
        
        # Use AgentCore browser navigation
        result = await client.navigate(url, session_id=session_id)
        
        return f"✅ Navigated to {url}. Title: {result.get('title', 'Unknown')}"
    except Exception as e:
        return f"❌ Navigation failed: {str(e)}"

@tool  
async def agentcore_screenshot(session_id: Optional[str] = None, full_page: bool = False) -> str:
    """Take screenshot using AgentCore Browser"""
    try:
        client = get_browser_client()
        
        # Create screenshots directory
        os.makedirs("screenshots", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/agentcore_{session_id or 'default'}_{timestamp}.png"
        
        # Take screenshot via AgentCore
        result = await client.screenshot(
            session_id=session_id,
            full_page=full_page,
            output_path=filename
        )
        
        return f"📸 Screenshot saved: {filename}"
    except Exception as e:
        return f"❌ Screenshot failed: {str(e)}"

@tool
async def agentcore_click(selector: str, session_id: Optional[str] = None) -> str:
    """Click element using AgentCore Browser"""
    try:
        client = get_browser_client()
        
        result = await client.click(selector, session_id=session_id)
        
        return f"👆 Clicked: {selector}"
    except Exception as e:
        return f"❌ Click failed: {str(e)}"

@tool
async def agentcore_fill(selector: str, text: str, session_id: Optional[str] = None) -> str:
    """Fill input using AgentCore Browser"""
    try:
        client = get_browser_client()
        
        result = await client.fill(selector, text, session_id=session_id)
        
        return f"✏️ Filled {selector} with text"
    except Exception as e:
        return f"❌ Fill failed: {str(e)}"

@tool
async def agentcore_get_content(selector: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """Get page content using AgentCore Browser"""
    try:
        client = get_browser_client()
        
        result = await client.get_text(selector=selector, session_id=session_id)
        content = result.get('text', '')
        
        # Truncate for display
        truncated = content[:500] + "..." if len(content) > 500 else content
        
        return f"📄 Content: {truncated}"
    except Exception as e:
        return f"❌ Get content failed: {str(e)}"

def cleanup_browser_client():
    """Clean up the browser client"""
    global _browser_client
    if _browser_client:
        _browser_client.stop()
        _browser_client = None
