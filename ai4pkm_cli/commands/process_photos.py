"""Report generation system with interactive inputs."""

from rich.console import Console


class ProcessPhotos:
    """Handles interactive report generation."""
    
    def __init__(self, logger):
        """Initialize report generator."""
        self.logger = logger
        self.console = Console()
        
    def process_photos(self):
        """Process photos with interactive user inputs."""
        import subprocess
        import glob
        import os
        try:
            subprocess.run(["osascript", "_Settings_/Scripts/export_photos.applescript"], check=True)
        except Exception as e:
            self.logger.error(f"Error exporting photos: {e}")

        try:
            # for all files under photostream run the script
            output_dir_path = "Ingest/Photolog/Snap/"
            for file in glob.glob("Photostream/*"):
                # check if same basename file exists in output_dir_path as filename
                basename = os.path.basename(file)
                if os.path.exists(os.path.join(output_dir_path, basename)):
                    continue
                subprocess.run(["_Settings_/Scripts/process_photo.sh", file, output_dir_path], check=True)
        except Exception as e:
            self.logger.error(f"Error processing photos: {e}")
            