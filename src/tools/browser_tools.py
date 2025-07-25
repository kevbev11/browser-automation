from typing import Optional
from langchain_core.tools import tool
from config.agentcore_config import agentcore_config
import asyncio

@tool
async def navigate_to_url(url: str, session_id: Optional[str] = None) -> str:
    """Navigate browser to a specific URL"""
    try:
        session = agentcore_config.get_browser_session(session_id)
        result = await session.navigate(url)
        
        # Store navigation in memory
        if agentcore_config.memory_client:
            agentcore_config.store_memory(
                session_id=session_id or "default",
                content=f"Navigated to {url}",
                metadata={
                    "action": "navigate", 
                    "url": url,
                    "timestamp": result.get("timestamp")
                }
            )
        
        return f"✅ Successfully navigated to {url}. Page title: {result.get('title', 'Unknown')}"
    except Exception as e:
        return f"❌ Error navigating to {url}: {str(e)}"

@tool
async def take_screenshot(session_id: Optional[str] = None, full_page: bool = False) -> str:
    """Take a screenshot of current page"""
    try:
        session = agentcore_config.get_browser_session(session_id)
        screenshot = await session.screenshot(full_page=full_page)
        
        return f"📸 Screenshot captured successfully. Image URL: {screenshot.get('url')}"
    except Exception as e:
        return f"❌ Error taking screenshot: {str(e)}"

@tool
async def click_element(selector: str, session_id: Optional[str] = None) -> str:
    """Click on an element using CSS selector"""
    try:
        session = agentcore_config.get_browser_session(session_id)
        result = await session.click(selector)
        
        return f"👆 Successfully clicked element: {selector}"
    except Exception as e:
        return f"❌ Error clicking element {selector}: {str(e)}"

@tool
async def fill_input(selector: str, text: str, session_id: Optional[str] = None) -> str:
    """Fill an input field with text"""
    try:
        session = agentcore_config.get_browser_session(session_id)
        result = await session.fill(selector, text)
        
        return f"✏️ Successfully filled input {selector} with provided text"
    except Exception as e:
        return f"❌ Error filling input {selector}: {str(e)}"

@tool
async def get_page_content(session_id: Optional[str] = None, selector: Optional[str] = None) -> str:
    """Get text content from page or specific element"""
    try:
        session = agentcore_config.get_browser_session(session_id)
        content = await session.get_content(selector=selector)
        
        # Truncate content for response
        truncated_content = content[:500] + "..." if len(content) > 500 else content
        
        return f"📄 Page content retrieved: {truncated_content}"
    except Exception as e:
        return f"❌ Error getting page content: {str(e)}"

@tool
async def wait_for_element(selector: str, timeout: int = 5000, session_id: Optional[str] = None) -> str:
    """Wait for an element to appear on the page"""
    try:
        session = agentcore_config.get_browser_session(session_id)
        result = await session.wait_for_selector(selector, timeout=timeout)
        
        return f"⏱️ Element {selector} appeared on page"
    except Exception as e:
        return f"❌ Element {selector} did not appear within {timeout}ms: {str(e)}"
