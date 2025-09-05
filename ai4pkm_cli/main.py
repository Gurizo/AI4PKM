#!/usr/bin/env python3
"""Main entry point for PKM CLI."""

import signal
import sys
import click
from .cli import PKMApp


def signal_handler(sig, frame):
    """Handle SIGINT (Ctrl+C) gracefully."""
    print("\n\nShutting down PKM CLI...")
    sys.exit(0)


@click.command()
@click.option('-p', '--prompt', help='Execute a one-time prompt')
def main(prompt):
    """PKM CLI - Personal Knowledge Management framework."""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize the PKM application
    app = PKMApp()
    
    if prompt:
        # Execute one-time prompt with log display
        import threading
        
        # Start log tail in background thread
        log_thread = threading.Thread(target=app._display_log_tail, daemon=True)
        log_thread.start()
        
        # Execute the prompt
        app.execute_prompt(prompt)
        
        # Give a moment for logs to display
        import time
        time.sleep(1)
    else:
        # Run continuously with cron jobs and log display
        app.run_continuous()


if __name__ == '__main__':
    main()

