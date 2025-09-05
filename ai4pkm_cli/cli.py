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
        self.logger = Logger(console_output=False)  # Disable console output for main logger
        self.claude_runner = ClaudeRunner(self.logger)
        self.cron_manager = CronManager(self.logger, self.claude_runner)
        self.report_generator = ReportGenerator(self.logger, self.claude_runner)
        self.running = False
        
    def execute_prompt(self, prompt):
        """Execute a one-time prompt."""
        self.logger.info(f"Executing prompt: {prompt}")
        
        if prompt.lower() == "generate_report":
            self.report_generator.generate_interactive_report()
        else:
            self.claude_runner.run_prompt(prompt.lower())
            
    def run_continuous(self):
        """Run continuously with cron jobs and log display."""
        self.running = True
        
        # Display welcome message
        self._display_welcome()
        
        # Start cron manager in background thread
        cron_thread = threading.Thread(target=self.cron_manager.start, daemon=True)
        cron_thread.start()
        
        # Start log tail display
        self._display_log_tail()
        
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
                prompts = job.get('prompts', [])
                prompts_str = ', '.join(prompts) if prompts else 'No prompts'
                self.console.print(f"  • {prompts_str} - {job['cron']}")
        else:
            self.console.print("\n[yellow]No cron jobs configured. Create cron.json to add jobs.[/yellow]")
        
        self.console.print("\n" + "="*60)
        self.console.print("[bold]Live Logs:[/bold]")
        self.console.print("="*60)
        
    def _display_log_tail(self):
        """Display real-time log tail."""
        try:
            self.logger.tail_logs(self.console)
        except KeyboardInterrupt:
            self.running = False
            self.cron_manager.stop()
            self.console.print("\n[yellow]PKM CLI stopped.[/yellow]")
