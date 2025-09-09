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
@click.option('-t', '--test', 'test_cron', is_flag=True, help='Test a specific cron job interactively')
def main(prompt, test_cron):
    """PKM CLI - Personal Knowledge Management framework."""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize the PKM application
    app = PKMApp()
    
    if prompt:
        # Execute the prompt
        app.execute_prompt(prompt)
    elif test_cron:
        # Test a specific cron job
        app.test_cron_job()
    else:
        # Run continuously with cron jobs and log display
        app.run_continuous()


if __name__ == '__main__':
    main()

