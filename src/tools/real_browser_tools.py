from typing import Optional, Dict, Any, List
from langchain_core.tools import tool
from playwright.async_api import async_playwright, Browser, Page
import asyncio
import os
from datetime import datetime

# Global browser management
_browser_sessions: Dict[str, Dict[str, Any]] = {}

async def get_browser_session(session_id: str = "default") -> Dict[str, Any]:
    """Get or create a browser session"""
    if session_id not in _browser_sessions:
        print(f"🌐 Creating new Chrome browser session: {session_id}")
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,  # Show the browser
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        _browser_sessions[session_id] = {
            'playwright': playwright,
            'browser': browser,
            'context': context,
            'page': page,
            'current_url': None
        }
    
    return _browser_sessions[session_id]

async def close_browser_session(session_id: str = "default"):
    """Close a browser session"""
    if session_id in _browser_sessions:
        session = _browser_sessions[session_id]
        await session['browser'].close()
        await session['playwright'].stop()
        del _browser_sessions[session_id]
        print(f"🔴 Closed browser session: {session_id}")

@tool
async def navigate_to_url(url: str, session_id: Optional[str] = None) -> str:
    """Navigate browser to a specific URL"""
    try:
        session_id = session_id or "default"
        session = await get_browser_session(session_id)
        page = session['page']
        
        print(f"🌐 Navigating to: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        # Wait a moment for page to settle
        await asyncio.sleep(2)
        
        title = await page.title()
        session['current_url'] = url
        
        return f"✅ Successfully navigated to {url}. Page title: {title}"
    except Exception as e:
        return f"❌ Error navigating to {url}: {str(e)}"

@tool
async def smart_click(description: str, session_id: Optional[str] = None) -> str:
    """Click on an element based on its description. Examples: 'search button', 'login link', 'submit button', 'sign up'"""
    try:
        session_id = session_id or "default"
        session = await get_browser_session(session_id)
        page = session['page']
        
        print(f"🎯 Looking for element to click: {description}")
        
        # Common selectors to try based on description
        desc_lower = description.lower()
        selectors_to_try = []
        
        if 'button' in desc_lower:
            if 'search' in desc_lower:
                selectors_to_try.extend([
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Search")',
                    'button:has-text("Go")',
                    '.search-button',
                    '#search-button'
                ])
            elif 'submit' in desc_lower:
                selectors_to_try.extend([
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Send")'
                ])
            elif 'login' in desc_lower or 'sign in' in desc_lower:
                selectors_to_try.extend([
                    'button:has-text("Login")',
                    'button:has-text("Sign in")',
                    'input[type="submit"]',
                    '.login-button'
                ])
            else:
                # Generic button search
                selectors_to_try.extend([
                    f'button:has-text("{description}")',
                    'button[type="submit"]',
                    'input[type="submit"]'
                ])
        
        elif 'link' in desc_lower:
            if 'login' in desc_lower or 'sign in' in desc_lower:
                selectors_to_try.extend([
                    'a:has-text("Login")',
                    'a:has-text("Sign in")',
                    'a:has-text("Log in")'
                ])
            else:
                selectors_to_try.extend([
                    f'a:has-text("{description}")',
                    f'a[href*="{desc_lower}"]'
                ])
        
        else:
            # Try to find any clickable element with the text
            selectors_to_try.extend([
                f'button:has-text("{description}")',
                f'a:has-text("{description}")',
                f'input[value*="{description}"]',
                f'*:has-text("{description}"):visible'
            ])
        
        # Try each selector
        for selector in selectors_to_try:
            try:
                print(f"   Trying selector: {selector}")
                element = await page.query_selector(selector)
                if element:
                    # Check if element is visible and clickable
                    is_visible = await element.is_visible()
                    if is_visible:
                        await element.click()
                        await asyncio.sleep(0.5)
                        return f"👆 Successfully clicked: {description} (using selector: {selector})"
            except Exception as e:
                print(f"   Selector {selector} failed: {e}")
                continue
        
        # If no specific selector worked, try a more general approach
        try:
            print(f"   Trying general text search for: {description}")
            await page.click(f'text="{description}"', timeout=5000)
            return f"👆 Successfully clicked: {description} (using text search)"
        except:
            pass
        
        return f"❌ Could not find clickable element: {description}"
        
    except Exception as e:
        return f"❌ Error clicking {description}: {str(e)}"

@tool
async def smart_fill(field_description: str, text: str, session_id: Optional[str] = None) -> str:
    """Fill an input field based on its description. Examples: 'search box', 'email field', 'password', 'username'"""
    try:
        session_id = session_id or "default"
        session = await get_browser_session(session_id)
        page = session['page']
        
        print(f"✏️ Looking for field to fill: {field_description} with '{text}'")
        
        # Common selectors based on field description
        desc_lower = field_description.lower()
        selectors_to_try = []
        
        if 'search' in desc_lower:
            selectors_to_try.extend([
                'input[name="q"]',
                'input[type="search"]',
                'input[placeholder*="search"]',
                '#search',
                '.search-input',
                'textarea[name="q"]'
            ])
        elif 'email' in desc_lower:
            selectors_to_try.extend([
                'input[type="email"]',
                'input[name="email"]',
                'input[name="custemail"]',
                'input[placeholder*="email"]'
            ])
        elif 'password' in desc_lower:
            selectors_to_try.extend([
                'input[type="password"]',
                'input[name="password"]',
                'input[name="pass"]'
            ])
        elif 'username' in desc_lower or 'user' in desc_lower:
            selectors_to_try.extend([
                'input[name="username"]',
                'input[name="user"]',
                'input[name="login"]'
            ])
        elif 'name' in desc_lower:
            selectors_to_try.extend([
                'input[name="name"]',
                'input[name="custname"]',
                'input[name="fullname"]',
                'input[placeholder*="name"]'
            ])
        elif 'phone' in desc_lower or 'tel' in desc_lower:
            selectors_to_try.extend([
                'input[type="tel"]',
                'input[name="phone"]',
                'input[name="tel"]',
                'input[name="custtel"]'
            ])
        else:
            # Generic input search
            selectors_to_try.extend([
                f'input[placeholder*="{field_description}"]',
                f'input[name*="{desc_lower}"]',
                'input[type="text"]',
                'textarea'
            ])
        
        # Try each selector
        for selector in selectors_to_try:
            try:
                print(f"   Trying selector: {selector}")
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        await element.fill("")  # Clear first
                        await element.fill(text)
                        await asyncio.sleep(0.5)
                        return f"✏️ Successfully filled {field_description} with text (using selector: {selector})"
            except Exception as e:
                print(f"   Selector {selector} failed: {e}")
                continue
        
        return f"❌ Could not find input field: {field_description}"
        
    except Exception as e:
        return f"❌ Error filling {field_description}: {str(e)}"

@tool
async def get_page_elements(session_id: Optional[str] = None) -> str:
    """Get a list of clickable elements and input fields on the current page"""
    try:
        session_id = session_id or "default"
        session = await get_browser_session(session_id)
        page = session['page']
        
        print("🔍 Analyzing page elements...")
        
        # Get clickable elements
        buttons = await page.query_selector_all('button, input[type="submit"], input[type="button"]')
        links = await page.query_selector_all('a[href]')
        inputs = await page.query_selector_all('input[type="text"], input[type="email"], input[type="search"], input[type="tel"], textarea')
        
        elements_info = []
        
        # Analyze buttons
        for button in buttons[:10]:  # Limit to first 10
            try:
                text = await button.text_content()
                tag_name = await button.evaluate('el => el.tagName')
                if text and text.strip():
                    elements_info.append(f"Button: '{text.strip()}'")
            except:
                pass
        
        # Analyze links
        for link in links[:10]:  # Limit to first 10
            try:
                text = await link.text_content()
                if text and text.strip():
                    elements_info.append(f"Link: '{text.strip()}'")
            except:
                pass
        
        # Analyze input fields
        for input_elem in inputs[:10]:  # Limit to first 10
            try:
                name = await input_elem.get_attribute('name')
                placeholder = await input_elem.get_attribute('placeholder')
                input_type = await input_elem.get_attribute('type')
                
                desc = f"Input field"
                if name:
                    desc += f" (name: {name})"
                if placeholder:
                    desc += f" (placeholder: {placeholder})"
                if input_type:
                    desc += f" (type: {input_type})"
                
                elements_info.append(desc)
            except:
                pass
        
        if elements_info:
            result = "📋 Found these elements:\n" + "\n".join(elements_info)
        else:
            result = "📋 No interactive elements found on this page"
        
        return result
        
    except Exception as e:
        return f"❌ Error analyzing page elements: {str(e)}"

@tool
async def take_screenshot(session_id: Optional[str] = None, full_page: bool = False) -> str:
    """Take a screenshot of current page"""
    try:
        session_id = session_id or "default"
        session = await get_browser_session(session_id)
        page = session['page']
        
        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/screenshot_{session_id}_{timestamp}.png"
        
        print(f"📸 Taking screenshot...")
        await page.screenshot(path=filename, full_page=full_page)
        
        return f"📸 Screenshot saved: {filename}"
    except Exception as e:
        return f"❌ Error taking screenshot: {str(e)}"

@tool
async def close_browser(session_id: Optional[str] = None) -> str:
    """Close the browser session"""
    try:
        session_id = session_id or "default"
        await close_browser_session(session_id)
        return f"🔴 Browser session {session_id} closed"
    except Exception as e:
        return f"❌ Error closing browser: {str(e)}"
