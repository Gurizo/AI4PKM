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
@click.option('-c', '--cron', 'run_cron', is_flag=True, help='Run continuous cron job scheduler')
@click.option('-a', '--agent', help='Set the AI agent to use (c/claude, g/gemini, o/codex)')
@click.option('--list-agents', is_flag=True, help='List available AI agents and their status')
@click.option('--show-config', is_flag=True, help='Show current configuration')
def main(prompt, test_cron, run_cron, agent, list_agents, show_config):
    """PKM CLI - Personal Knowledge Management framework."""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize the PKM application
    app = PKMApp()
    
    if list_agents:
        # List available agents
        app.list_agents()
    elif show_config:
        # Show current configuration
        app.show_config()
    elif agent and not prompt:
        # Set the global agent (only when no prompt specified)
        app.set_agent(agent)
    elif prompt:
        # Execute the prompt (with optional agent for this execution only)
        app.execute_prompt(prompt, agent)
    elif test_cron:
        # Test a specific cron job
        app.test_cron_job()
    elif run_cron:
        # Run continuously with cron jobs and log display
        app.run_continuous()
    else:
        # Show default information (config and instructions)
        app.show_default_info()


if __name__ == '__main__':
    main()

