import sys
import os
import asyncio
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.browser_agent import BrowserAutomationAgent
from config.settings import settings
from rich.console import Console
from rich.panel import Panel

console = Console()

class SimplifiedAgentCoreDemo:
    """Simplified demo using your existing LangGraph agent"""
    
    def __init__(self):
        self.agent = None
        
    def setup_agent(self):
        """Setup LangGraph agent"""
        console.print("[cyan]🤖 Setting up LangGraph Agent...[/cyan]")
        
        try:
            self.agent = BrowserAutomationAgent()
            console.print("[green]✅ LangGraph Agent initialized[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Failed to setup agent: {e}[/red]")
            raise
    
    async def run_task(self, task: str, session_id: str = "demo"):
        """Run a browser automation task"""
        console.print(f"\n[bold blue]🎯 Executing task:[/bold blue] {task}")
        
        try:
            with console.status("[bold green]Running automation...[/bold green]", spinner="dots"):
                result = await self.agent.run_task(task, session_id=session_id)
            
            if result.get("messages"):
                last_message = result["messages"][-1]
                console.print(f"[green]✅ Result: {last_message.content}[/green]")
            
            # Show all messages for debugging
            console.print(f"\n[dim]📊 Total messages: {len(result.get('messages', []))}[/dim]")
            for i, msg in enumerate(result.get("messages", []), 1):
                msg_type = type(msg).__name__
                content = getattr(msg, 'content', 'No content')[:100]
                console.print(f"[dim]  {i}. {msg_type}: {content}...[/dim]")
            
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
        console.print("[dim]Examples:[/dim]")
        console.print("[dim]  - Navigate to https://example.com and take a screenshot[/dim]")
        console.print("[dim]  - Navigate to google.com and search for 'LangGraph'[/dim]")
        console.print("[dim]  - Fill a form on httpbin.org[/dim]")
        
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

async def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="LangGraph Browser Agent Demo")
    parser.add_argument("--task", help="Specific task to run")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Display welcome banner
    console.print(
        Panel(
            "[bold cyan]LangGraph Browser Agent Demo[/bold cyan]\n\n"
            "This demonstrates:\n"
            "• LangGraph workflow orchestration\n"
            "• OpenAI GPT model integration\n"
            "• Mock browser automation tools\n"
            "• Interactive task execution\n\n"
            "[yellow]Note: Using mock browser tools for demo[/yellow]",
            title="🚀 Browser Automation Demo",
            border_style="blue"
        )
    )
    
    demo = SimplifiedAgentCoreDemo()
    
    try:
        # Setup agent
        demo.setup_agent()
        
        console.print(f"\n[green]🎉 Demo ready![/green]")
        console.print(f"[cyan]Model: {settings.model_name}[/cyan]")
        console.print(f"[cyan]Using: Mock browser tools[/cyan]")
        
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
                "Navigate to https://google.com and search for 'LangGraph browser automation'",
                "Take a screenshot of the search results and get the page title"
            ]
            
            for i, task in enumerate(demo_tasks, 1):
                console.print(f"\n[bold]📋 Demo Task {i}/{len(demo_tasks)}[/bold]")
                await demo.predefined_demo(task)
                await asyncio.sleep(1)  # Pause between tasks
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo failed: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
