import sys
import os
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.browser_agent import BrowserAutomationAgent
import json

async def test_detailed():
    """Detailed test to see what the agent is doing"""
    print("🧪 Detailed Browser Agent Test")
    print("=" * 60)
    
    agent = BrowserAutomationAgent()
    
    # Simple task
    task = "Navigate to https://example.com and take a screenshot"
    print(f"\n🎯 Task: {task}")
    print("-" * 60)
    
    try:
        result = await agent.run_task(task, session_id="detailed_test")
        
        print(f"\n📊 Raw Result Type: {type(result)}")
        print(f"📊 Result Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            # Print all messages
            if "messages" in result:
                print(f"\n💬 Messages ({len(result['messages'])}):")
                for i, msg in enumerate(result["messages"]):
                    print(f"  {i+1}. Type: {type(msg).__name__}")
                    print(f"     Content: {getattr(msg, 'content', 'No content')[:200]}...")
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        print(f"     Tool Calls: {len(msg.tool_calls)} tools called")
                        for j, tool_call in enumerate(msg.tool_calls):
                            print(f"       {j+1}. {tool_call.get('name', 'Unknown tool')}")
            
            # Print other state
            for key, value in result.items():
                if key != "messages":
                    print(f"\n🔧 {key}: {value}")
        
        print(f"\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_detailed())
