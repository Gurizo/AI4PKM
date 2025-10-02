"""Report generation system with interactive inputs."""

import os
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
# Agent will be passed in directly, no need to import
from ..utils import interactive_select


class GenerateReport:
    """Handles interactive report generation."""
    
    def __init__(self, logger, agent):
        """Initialize report generator."""
        self.logger = logger
        self.console = Console()
        self.agent = agent
        
    def generate_interactive_report(self):
        """Generate a report with an improved, context-aware interactive workflow."""
        self.console.print("\n[bold blue]Generate Report[/bold blue]")
        
        try:
            event_name = None
            data_sources = []

            # 1. Select a template first
            all_templates = self._get_available_templates()
            if not all_templates:
                self.console.print("\n[yellow]No templates found in _Settings_/Templates/ or any event folders.[/yellow]")
                return

            template_name = interactive_select(
                all_templates, 
                "Select a Report Template",
                self.console
            )

            # 2. Conditionally select an event if the template suggests it
            if "event" in template_name.lower() or "festival" in template_name.lower():
                events = self._get_available_events()
                if not events:
                    self.console.print("\n[yellow]No events found in Events/ directory, but the template seems to require one.[/yellow]")
                else:
                    event_name = interactive_select(
                        events, 
                        "Select the Event for this Report",
                        self.console
                    )
                    
                    # Set data sources based on the selected event
                    potential_sources = [f"Events/{event_name}/processed_data"]
                    data_sources = [path for path in potential_sources if os.path.exists(path) and os.path.isdir(path)]
                    
                    if not data_sources:
                        self.console.print("\n[yellow]No processed_data directory found for the selected event. Report generation might be incomplete.[/yellow]")

            # 3. Load the template content from the correct location
            template_path = None
            if event_name:
                # Prioritize event-specific template
                for ext in ['.md', '.txt']:
                    path = f"Events/{event_name}/{template_name}{ext}"
                    if os.path.exists(path):
                        template_path = path
                        break
            
            if not template_path:
                # Fallback to global template
                global_path = f"_Settings_/Templates/{template_name}.md"
                if os.path.exists(global_path):
                    template_path = global_path
            
            if not template_path:
                self.logger.error(f"Template file '{template_name}' not found in event or global template directories.")
                return
                
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # 4. Generate the report by sending the template content directly as the prompt
            report_base_name = f"{event_name} Report" if event_name else f"{template_name}"
            self.logger.info(f"Generating report from template '{template_name}'...")
            
            # Prepare the final prompt by injecting data_sources directly into the template content
            final_prompt = template_content.format(data_sources=data_sources)
            
            result = self.agent.run_prompt(inline_prompt=final_prompt)
            report_content = result[0] if result and result[0] else None
            
            if report_content:
                report_filename = self._save_report(report_base_name, report_content)
                self.logger.info(f"Report saved to: {report_filename}")
            else:
                self.logger.error("Failed to generate report content.")
                
        except KeyboardInterrupt:
            self.logger.warning("Report generation cancelled.")
        except Exception as e:
            self.logger.error(f"An error occurred during report generation: {e}")

    def _get_available_events(self):
        """Get list of available events."""
        events_dir = "Events"
        if not os.path.exists(events_dir):
            return []
            
        events = []
        for item in os.listdir(events_dir):
            if os.path.isdir(os.path.join(events_dir, item)):
                events.append(item)
                
        return sorted(events)

    def _get_available_templates(self, event_name=None):
        """
        Get a combined list of available templates.
        If event_name is provided, it includes templates from that specific event and global ones.
        If event_name is None, it includes templates from ALL events and global templates.
        """
        templates = set()

        # Helper to add templates from a directory, removing the extension
        def find_templates_in_dir(directory, extensions):
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    if file.endswith(extensions):
                        templates.add(os.path.splitext(file)[0])

        # Find global templates
        find_templates_in_dir("_Settings_/Templates", ('.md',))

        # Find event-specific templates
        events_dir = "Events"
        if os.path.exists(events_dir):
            if event_name:
                # Find from a specific event folder if provided
                find_templates_in_dir(os.path.join(events_dir, event_name), ('.md', '.txt'))
            else:
                # Find from all event folders for the initial listing
                for event in os.listdir(events_dir):
                    event_path = os.path.join(events_dir, event)
                    if os.path.isdir(event_path):
                        find_templates_in_dir(event_path, ('.md', '.txt'))
        
        return sorted(list(templates))
        
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
