"""Main PKM CLI application class."""

import os
import threading
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .cron_manager import CronManager
from .logger import Logger
from .claude_runner import ClaudeRunner
from .prompt_runners.report_generator import ReportGenerator


class PKMApp:
    """Main PKM CLI application."""
    
    def __init__(self):
        """Initialize the PKM application."""
        self.console = Console()
        self.logger = Logger(console_output=True)  # Enable console output for main logger
        self.claude_runner = ClaudeRunner(self.logger)
        self.running = False

    def execute_prompt(self, prompt):
        """Execute a one-time prompt."""
        self.logger.info(f"Executing prompt: {prompt}")
        
        if prompt.lower() == "generate_report":
            report_generator = ReportGenerator(self.logger, self.claude_runner)
            report_generator.generate_interactive_report()
        else:
            result, _ = self.claude_runner.run_prompt(prompt_name=f"Adhoc/{prompt.lower()}")
            self.logger.info(result)
            
    def run_continuous(self):
        """Run continuously with cron jobs and log display."""
        self.running = True
        self.cron_manager = CronManager(self.logger, self.claude_runner)
        
        # Display welcome message
        self._display_welcome()
        
        self.cron_manager.start()
        
    def _display_welcome(self):
        """Display welcome message and status."""
        welcome_text = Text()
        welcome_text.append("PKM CLI - Personal Knowledge Management\n", style="bold blue")
        welcome_text.append(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", style="dim")
        welcome_text.append("Press Ctrl+C to stop\n", style="dim")
        
        panel = Panel(welcome_text, title="PKM CLI", border_style="blue")
        self.console.print(panel)
        
        # Display cron job status
        jobs = self.cron_manager.get_jobs()
        if jobs:
            self.console.print(f"\n[green]Loaded {len(jobs)} cron jobs:[/green]")
            for job in jobs:
                inline_prompt = job.get('inline_prompt')
                self.console.print(f"  • {inline_prompt} - {job['cron']}")
        else:
            self.console.print("\n[yellow]No cron jobs configured. Create cron.json to add jobs.[/yellow]")
        
        self.console.print("\n" + "="*60)
        self.console.print("[bold]Live Logs:[/bold]")
        self.console.print("="*60)