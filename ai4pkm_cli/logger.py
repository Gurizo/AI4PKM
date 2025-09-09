"""Logging system with file output and real-time tail display."""

import os
import time
from datetime import datetime
from threading import Lock
from rich.console import Console
from rich.text import Text


class Logger:
    """Logger that writes to logs.txt and supports real-time tail display."""
    
    def __init__(self, log_file=None, console_output=True):
        """Initialize logger."""
        if log_file is None:
            # Find project root (directory containing this file's parent)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)  # Go up from ai4pkm_cli/ to project root
            
            # Create logs directory path
            logs_dir = os.path.join(project_root, "_Settings_", "Logs")
            
            # Ensure logs directory exists
            os.makedirs(logs_dir, exist_ok=True)
            
            # Create date-based log filename with ai4pkm prefix
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(logs_dir, f"ai4pkm_{date_str}.log")
        
        self.log_file = log_file
        self.lock = Lock()
        self.console_output = console_output
        self.console = Console() if console_output else None
        self._ensure_log_file()
        
    def _ensure_log_file(self):
        """Ensure log file exists and clear it for fresh start."""
        with open(self.log_file, 'w') as f:
            f.write(f"PKM CLI Log - Started at {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n")
                
    def _write_log(self, level, message):
        """Write log entry to file and optionally to console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        with self.lock:
            # Write to file
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
            
            # Also print to console if enabled
            if self.console_output and self.console:
                self._display_log_line(self.console, log_entry.rstrip())
                
    def info(self, message):
        """Log info message."""
        self._write_log("INFO", message)
        
    def error(self, message):
        """Log error message."""
        self._write_log("ERROR", message)
        
    def warning(self, message):
        """Log warning message."""
        self._write_log("WARNING", message)
        
    def debug(self, message):
        """Log debug message."""
        self._write_log("DEBUG", message)

    def _display_log_line(self, console, line):
        """Display a single log line with appropriate styling."""
        if not line.strip():
            return
            
        text = Text()
        
        # Parse log line format: [timestamp] LEVEL: message
        if "] " in line and ": " in line:
            try:
                timestamp_part = line.split("] ")[0] + "]"
                rest = line.split("] ", 1)[1]
                level_part = rest.split(": ")[0]
                message_part = rest.split(": ", 1)[1]
                
                # Style timestamp
                text.append(timestamp_part, style="dim")
                text.append(" ")
                
                # Style level with colors
                if level_part == "ERROR":
                    text.append(level_part, style="bold red")
                elif level_part == "WARNING":
                    text.append(level_part, style="bold yellow")
                elif level_part == "INFO":
                    text.append(level_part, style="bold green")
                elif level_part == "DEBUG":
                    text.append(level_part, style="bold blue")
                else:
                    text.append(level_part, style="bold")
                    
                text.append(": ")
                text.append(message_part)
                
            except (IndexError, ValueError):
                # If parsing fails, display line as-is
                text.append(line)
        else:
            text.append(line)
            
        console.print(text)
