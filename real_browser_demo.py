import sys
import os
import asyncio
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.real_browser_agent import RealBrowserAutomationAgent
from rich.console import Console
from rich.panel import Panel

console = Console()

class RealBrowserDemo:
    """Demo that opens and controls a real Chrome browser"""
    
    def __init__(self):
        self.agent = None
        
    def setup_agent(self):
        """Setup real browser agent"""
        console.print("[cyan]🌐 Setting up Real Browser Agent...[/cyan]")
        
        try:
            self.agent = RealBrowserAutomationAgent()
            console.print("[green]✅ Real Browser Agent initialized[/green]")
            console.print("[yellow]📌 Chrome browser will open when first task starts[/yellow]")
            
        except Exception as e:
            console.print(f"[red]❌ Failed to setup agent: {e}[/red]")
            raise
    
    async def run_task(self, task: str, session_id: str = "demo"):
        """Run a browser automation task with real browser"""
        console.print(f"\n[bold blue]🎯 Executing task:[/bold blue] {task}")
        console.print("[dim]👀 Watch the Chrome browser window for actions[/dim]")
        
        try:
            with console.status("[bold green]Running automation...[/bold green]", spinner="dots"):
                result = await self.agent.run_task(task, session_id=session_id)
            
            if result.get("messages"):
                last_message = result["messages"][-1]
                console.print(f"[green]✅ Result: {last_message.content}[/green]")
            
            return result
            
        except Exception as e:
            console.print(f"[red]❌ Task failed: {e}[/red]")
            return None
    
    async def interactive_demo(self):
        """Interactive demo with real browser"""
        console.print("\n[bold cyan]🎮 Interactive Mode - Real Browser[/bold cyan]")
        console.print("[yellow]Enter browser automation tasks (or 'quit' to exit)[/yellow]")
        console.print("[dim]Working examples:[/dim]")
        console.print("[dim]  - Navigate to https://example.com and take a screenshot[/dim]")
        console.print("[dim]  - Navigate to httpbin.org/forms/post and fill the custname field with 'John Doe'[/dim]")
        console.print("[dim]  - close_browser (when done)[/dim]")
        
        session_id = "interactive_session"
        
        while True:
            try:
                task = input("\n🎯 Enter task: ").strip()
                
                if task.lower() in ['quit', 'exit', 'q']:
                    console.print("[yellow]🔴 Closing browser...[/yellow]")
                    await self.run_task("close_browser", session_id)
                    break
                
                if not task:
                    continue
                
                await self.run_task(task, session_id)
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]🔴 Closing browser...[/yellow]")
                try:
                    await self.agent.cleanup(session_id)
                except:
                    pass
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    async def working_demo(self):
        """Demo with tasks that actually work"""
        session_id = "working_demo"
        
        working_tasks = [
            "Navigate to https://example.com and take a screenshot",
            "Navigate to https://httpbin.org/forms/post",
            "Take a screenshot of the form page",
            "Fill the input field with name 'custname' with the text 'John Doe'",
            "Fill the input field with name 'custemail' with the text 'john@example.com'", 
            "Take a screenshot of the filled form",
            "close_browser"
        ]
        
        console.print(f"\n[bold green]🎯 Running Working Demo with {len(working_tasks)} tasks[/bold green]")
        
        for i, task in enumerate(working_tasks, 1):
            console.print(f"\n[bold]📋 Task {i}/{len(working_tasks)}:[/bold] {task}")
            await self.run_task(task, session_id)
            
            if i < len(working_tasks):
                console.print("[dim]⏱️  Pausing 2 seconds...[/dim]")
                await asyncio.sleep(2)

async def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="Real Browser LangGraph Demo")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    console.print(
        Panel(
            "[bold cyan]Real Browser LangGraph Demo[/bold cyan]\n\n"
            "This will:\n"
            "• Open a real Chrome browser window\n"
            "• Use LangGraph to orchestrate actions\n"
            "• Show you actual browser automation\n"
            "• Take screenshots and save them\n\n"
            "[green]✨ You'll see the browser in action![/green]",
            title="🌐 Real Browser Demo",
            border_style="green"
        )
    )
    
    demo = RealBrowserDemo()
    
    try:
        demo.setup_agent()
        
        console.print(f"\n[green]🎉 Demo ready![/green]")
        console.print(f"[cyan]📂 Screenshots will be saved to: screenshots/[/cyan]")
        
        if args.interactive:
            await demo.interactive_demo()
        else:
            await demo.working_demo()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo failed: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(main())
