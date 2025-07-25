import asyncio
from rich.console import Console

console = Console()

async def test_agentcore_import():
    """Test if AgentCore components are available"""
    console.print("[cyan]🔍 Testing AgentCore imports...[/cyan]")
    
    try:
        from bedrock_agentcore.tools.browser_client import BrowserClient
        console.print("[green]✅ BrowserClient import successful[/green]")
        
        # Try to create a client (doesn't start it)
        client = BrowserClient("us-west-2")
        console.print("[green]✅ BrowserClient creation successful[/green]")
        
        console.print("[yellow]💡 Ready for real AgentCore demo![/yellow]")
        return True
        
    except ImportError as e:
        console.print(f"[red]❌ Import failed: {e}[/red]")
        console.print("[yellow]💡 Use the simplified demo instead[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]❌ AgentCore test failed: {e}[/red]")
        console.print("[yellow]💡 Check AWS credentials and region[/yellow]")
        return False

if __name__ == "__main__":
    asyncio.run(test_agentcore_import())
