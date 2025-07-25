import sys
import os
sys.path.insert(0, 'src')

try:
    import bedrock_agentcore
    import langgraph
    import langchain_openai
    from langchain_openai import ChatOpenAI
    print("✅ All packages imported successfully!")
    print("✅ OpenAI integration ready!")
    print("🎉 Setup is complete!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Run: pip install -r requirements.txt")
