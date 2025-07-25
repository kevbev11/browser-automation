import sys
import os
import asyncio
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bedrock_agentcore.tools.browser_client import BrowserClient
from langchain_aws import ChatBedrockConverse
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from contextlib import suppress
from agents.browser_agent import BrowserAutomationAgent
from config.settings import settings
from boto3.session import Session

console = Console()

class AgentCoreLiveDemo:
    """Live demo using real AWS AgentCore Browser with LangGraph"""
    
    def __init__(self, region="us-west-2"):
        self.region = region
        self.client = None
        self.agent = None
        
    async def setup_browser_client(self):
        """Initialize the AgentCore browser client"""
        console.print("[cyan]🔄 Initializing AgentCore Browser Client...[/cyan]")
        
        try:
            # Create and start browser client
            self.client = BrowserClient(self.region)
            self.client.start()
            
            console.print("[green]✅ AgentCore Browser Client started[/green]")
            
            # Get WebSocket URL and headers
            ws_url, headers = self.client.generate_ws_headers()
            
            console.print(f"[cyan]🌐 WebSocket URL: {ws_url}[/cyan]")
            
            return ws_url, headers
            
        except Exception as e:
            console.print(f"[red]❌ Failed to setup browser client: {e}[/red]")
            raise
    
    def setup_agent(self):
        """Setup LangGraph agent with OpenAI"""
        console.print("[cyan]🤖 Setting up LangGraph Agent...[/cyan]")
        
        try:
            # Use your existing LangGraph agent
            self.agent = BrowserAutomationAgent()
            console.print("[green]✅ LangGraph Agent initialized[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Failed to setup agent: {e}[/red]")
            raise
    
    async def run_task(self, task: str, session_id: str = "live_demo"):
        """Run a browser automation task"""
        console.print(f"\n[bold blue]🎯 Executing task:[/bold blue] {task}")
        
        try:
            with console.status("[bold green]Running automation...[/bold green]", spinner="dots"):
                result = await self.agent.run_task(task, session_id=session_id)
            
            if result.get("messages"):
                last_message = result["messages"][-1]
                console.print(f"[green]✅ Result: {last_message.content}[/green]")
            
            return result
            
        except Exception as e:
            console.print(f"[red]❌ Task failed: {e}[/red]")
            import traceback
            traceback.print_exc()
            return None
    
    async def interactive_demo(self):
        """Interactive demo where user can input tasks"""
        console.print("\n[bold cyan]🎮 Interactive Mode[/bold cyan]")
        console.print("[yellow]Enter browser automation tasks (or 'quit' to exit)[/yellow]")
        
        session_id = "interactive_session"
        
        while True:
            try:
                task = input("\n🎯 Enter task: ").strip()
                
                if task.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not task:
                    continue
                
                await self.run_task(task, session_id)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    async def predefined_demo(self, task: str):
        """Run a predefined task"""
        await self.run_task(task)
    
    def cleanup(self):
        """Clean up resources"""
        console.print("\n[yellow]🧹 Cleaning up...[/yellow]")
        
        if self.client:
            try:
                self.client.stop()
                console.print("[green]✅ Browser client stopped[/green]")
            except Exception as e:
                console.print(f"[red]❌ Error stopping client: {e}[/red]")

async def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="AgentCore + LangGraph Live Demo")
    parser.add_argument("--task", help="Specific task to run")
    parser.add_argument("--region", default="us-west-2", help="AWS region")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Display welcome banner
    console.print(
        Panel(
            "[bold cyan]AgentCore + LangGraph Live Demo[/bold cyan]\n\n"
            "This demonstrates:\n"
            "• Real AWS AgentCore Browser Tool\n"
            "• LangGraph workflow orchestration\n"
            "• OpenAI GPT-4 model integration\n"
            "• Live browser automation\n\n"
            "[yellow]Requirements: AWS credentials configured[/yellow]",
            title="🚀 Browser Automation Demo",
            border_style="blue"
        )
    )
    
    demo = AgentCoreLiveDemo(region=args.region)
    
    try:
        # Setup browser client
        ws_url, headers = await demo.setup_browser_client()
        
        # Setup agent
        demo.setup_agent()
        
        console.print(f"\n[green]🎉 Demo ready![/green]")
        console.print(f"[cyan]Region: {args.region}[/cyan]")
        console.print(f"[cyan]WebSocket: {ws_url}[/cyan]")
        
        if args.interactive:
            # Interactive mode
            await demo.interactive_demo()
        elif args.task:
            # Single task mode
            await demo.predefined_demo(args.task)
        else:
            # Default demo tasks
            demo_tasks = [
                "Navigate to https://example.com and take a screenshot",
                "Navigate to https://google.com and search for 'AWS AgentCore'",
                "Take a screenshot of the search results"
            ]
            
            for i, task in enumerate(demo_tasks, 1):
                console.print(f"\n[bold]Demo Task {i}/{len(demo_tasks)}[/bold]")
                await demo.predefined_demo(task)
                await asyncio.sleep(2)  # Pause between tasks
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo failed: {e}[/red]")
        import traceback
        traceback.print_exc()
    finally:
        demo.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
