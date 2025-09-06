"""Common utilities for PKM CLI."""

import sys
import termios
import tty
from rich.console import Console


def interactive_select(options, title="Select an option", console=None):
    """Interactive selection menu with arrow key navigation."""
    if console is None:
        console = Console()
        
    selected = 0
    
    while True:
        # Clear screen and show menu
        console.clear()
        console.print(f"\n[bold blue]{title}[/bold blue]")
        console.print("Use ↑/↓ arrow keys to navigate, Enter to select\n")
        
        for i, option in enumerate(options):
            if i == selected:
                console.print(f"[bold green]→ {option}[/bold green]")
            else:
                console.print(f"  {option}")
        
        # Get user input
        try:
            # Save terminal settings
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(sys.stdin.fileno())
            
            # Read key
            key = sys.stdin.read(1)
            
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
            if key == '\x1b':  # ESC sequence
                key += sys.stdin.read(2)
                if key == '\x1b[A':  # Up arrow
                    selected = (selected - 1) % len(options)
                elif key == '\x1b[B':  # Down arrow
                    selected = (selected + 1) % len(options)
            elif key == '\r' or key == '\n':  # Enter
                return options[selected]
            elif key == '\x03':  # Ctrl+C
                raise KeyboardInterrupt
                
        except (termios.error, OSError):
            # Fallback for environments that don't support termios
            console.print("\n[yellow]Arrow key navigation not supported in this environment.[/yellow]")
            console.print("Available options:")
            for i, option in enumerate(options, 1):
                console.print(f"  {i}. {option}")
            
            while True:
                try:
                    choice = int(input(f"Select option (1-{len(options)}): ")) - 1
                    if 0 <= choice < len(options):
                        return options[choice]
                    else:
                        print(f"Please enter a number between 1 and {len(options)}")
                except ValueError:
                    print("Please enter a valid number")
                except KeyboardInterrupt:
                    raise
