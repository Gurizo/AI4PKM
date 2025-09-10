"""Report generation system with interactive inputs."""

import os
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
# Agent will be passed in directly, no need to import
from ..utils import interactive_select


class ReportGenerator:
    """Handles interactive report generation."""
    
    def __init__(self, logger, agent):
        """Initialize report generator."""
        self.logger = logger
        self.console = Console()
        self.agent = agent
        
    def generate_interactive_report(self):
        """Generate a report with interactive user inputs."""
        self.console.print("\n[bold blue]Generate Report[/bold blue]")
        self.console.print("Please provide the following information:")
        
        try:
            # Calculate default times (start and end of today)
            today = datetime.now()
            start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=0)
            
            default_start = start_of_day.strftime("%Y-%m-%d %H:%M")
            default_end = end_of_day.strftime("%Y-%m-%d %H:%M")
            
            # Get user inputs
            start_time = Prompt.ask(
                "\n[cyan]Start time[/cyan] (YYYY-MM-DD HH:MM)", 
                default=default_start
            )
            end_time = Prompt.ask(
                "[cyan]End time[/cyan] (YYYY-MM-DD HH:MM)", 
                default=default_end
            )
            name = Prompt.ask("[cyan]Name[/cyan]")
            description = Prompt.ask("[cyan]Description of the activity[/cyan]")
            
            # Interactive template selection
            templates = self._get_available_templates()
            if templates:
                template_options = templates
                template_name = interactive_select(
                    template_options, 
                    "Select Template",
                    self.console
                )
            else:
                self.console.print("\n[yellow]No templates found in _Settings_/Templates/ directory[/yellow]")
                template_name = Prompt.ask("[cyan]Template name[/cyan]")
            
            # Generate the report
            self.logger.info(f"Generating report '{name}'...")
            
            # Load the template content
            template_file = f"_Settings_/Templates/{template_name}.md"
            if not os.path.exists(template_file):
                self.logger.error(f"Template file not found: {template_file}")
                return
                
            with open(template_file, 'r') as f:
                template_content = f.read()
            
            # Prepare parameters for the prompt
            params = {
                "name": name,
                "description": description,
                "start_time": start_time,
                "end_time": end_time,
                "template_name": template_name,
                "template_content": template_content,
                "timestamp": datetime.now().isoformat()
            }
            
            # Run the prompt with parameters
            result = self.agent.run_prompt(prompt_name="Adhoc/generate_report", params=params)
            report_content = result[0] if result and result[0] else None
            
            if report_content:
                # Save the report
                report_filename = self._save_report(name, report_content)
                self.logger.info(f"Report saved to: {report_filename}")
            else:
                self.logger.error("Failed to generate report")
                
        except KeyboardInterrupt:
            self.logger.warning("Report generation cancelled")
        except Exception as e:
            self.logger.error(f"Report generation error: {e}")
            
    def _get_available_templates(self):
        """Get list of available templates."""
        templates_dir = "_Settings_/Templates"
        if not os.path.exists(templates_dir):
            return []
            
        templates = []
        for file in os.listdir(templates_dir):
            if file.endswith('.md'):
                templates.append(file[:-3])  # Remove .md extension
                
        return sorted(templates)
        
    def _save_report(self, name, content):
        """Save the generated report to the Reports directory."""
        # Create Reports directory if it doesn't exist
        reports_dir = "Reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d")
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '-').lower()
        
        filename = f"{timestamp}-{safe_name}.md"
        filepath = os.path.join(reports_dir, filename)
        
        # Handle duplicate filenames
        counter = 1
        original_filepath = filepath
        while os.path.exists(filepath):
            base, ext = os.path.splitext(original_filepath)
            filepath = f"{base}-{counter}{ext}"
            counter += 1
            
        # Write the report
        with open(filepath, 'w') as f:
            f.write(content)
            
        return filepath
