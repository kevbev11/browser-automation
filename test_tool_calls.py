import sys
import os
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.browser_agent import BrowserAutomationAgent

async def test_tool_calls():
    """Test to see if tools are actually being called"""
    print("🔧 Testing Tool Calls")
    print("=" * 40)
    
    agent = BrowserAutomationAgent()
    
    # Very simple, direct task
    task = "Use the navigate_to_url tool to go to https://example.com"
    print(f"\n🎯 Task: {task}")
    print("-" * 40)
    
    try:
        result = await agent.run_task(task, session_id="tool_test")
        
        print(f"\n📊 Total messages: {len(result['messages'])}")
        
        for i, msg in enumerate(result["messages"]):
            print(f"\n💬 Message {i+1}: {type(msg).__name__}")
            print(f"   Content: {getattr(msg, 'content', 'No content')[:100]}...")
            
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                print(f"   🔧 Tool Calls: {len(msg.tool_calls)}")
                for j, tool_call in enumerate(msg.tool_calls):
                    print(f"      {j+1}. Function: {tool_call.get('name', 'Unknown')}")
                    print(f"         Args: {tool_call.get('args', {})}")
            else:
                print("   🔧 No tool calls in this message")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tool_calls())
