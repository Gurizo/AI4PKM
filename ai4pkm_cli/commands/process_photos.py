"""Report generation system with interactive inputs."""

from rich.console import Console


class ProcessPhotos:
    """Handles photo processing with configurable source and destination folders."""

    def __init__(self, logger, config=None):
        """Initialize photo processor."""
        self.logger = logger
        self.console = Console()
        self.config = config

    def process_photos(self):
        """Process photos with configurable source and destination folders."""
        import subprocess
        import glob
        import os

        # Get configurable paths and settings
        if self.config:
            source_folder = self.config.get_photo_source_folder()
            destination_folder = self.config.get_photo_destination_folder()
            albums = self.config.get_photo_albums()
            days = self.config.get_photo_days()
        else:
            # Fallback to hardcoded paths if no config
            source_folder = "Ingest/Photolog/Original/"
            destination_folder = "Ingest/Photolog/Processed/"
            albums = ["AI4PKM"]
            days = 7

        self.logger.info(
            f"Processing photos from: {source_folder} -> {destination_folder}"
        )
        self.logger.info(f"Albums to process: {albums}")
        self.logger.info(f"Looking back {days} days")

        # Export photos using AppleScript - process each album
        try:
            # Get the script path relative to the package root
            script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "export_photos.applescript")
            script_path = os.path.abspath(script_path)
            
            if not os.path.exists(script_path):
                self.logger.error(f"AppleScript not found: {script_path}")
                return
            
            self.logger.info("Exporting photos from Photos app...")
            
            # Process each album in the list
            for album in albums:
                self.logger.info(f"Processing album: {album}")
                result = subprocess.run(
                    ["osascript", script_path, album, source_folder, str(days)], 
                    capture_output=True, text=True, check=True
                )
                
                # Log AppleScript output for debugging
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            self.logger.info(f"AppleScript ({album}): {line.strip()}")
                            
            self.logger.info("Photo export completed successfully for all albums")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"AppleScript execution failed for album {album}: {e}")
            self.logger.error(f"Error output: {e.stderr}")
            return
        except Exception as e:
            self.logger.error(f"Error exporting photos: {e}")
            return

        try:
            # Ensure destination directory exists
            os.makedirs(destination_folder, exist_ok=True)

            # Process all files in the source folder
            processed_basenames = set()
            source_pattern = os.path.join(source_folder, "*")
            processed_count = 0
            skipped_count = 0

            for file in glob.glob(source_pattern):
                if not os.path.isfile(file):
                    continue

                # Check if same basename file exists in destination folder
                basename = os.path.basename(file)
                basename_no_ext = os.path.splitext(basename)[0]

                if basename_no_ext in processed_basenames:
                    continue

                processed_basenames.add(basename_no_ext)

                # Check for any file whose name starts with basename_no_ext exists
                file_path = os.path.join(destination_folder, f"{basename_no_ext}")
                files = glob.glob(f"{file_path}*")
                if files:
                    skipped_count += 1
                    continue

                # Get the processing script path
                script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "process_photo.sh")
                script_path = os.path.abspath(script_path)
                
                if not os.path.exists(script_path):
                    self.logger.error(f"Processing script not found: {script_path}")
                    continue
                
                self.logger.info(f"Processing: {basename}")
                try:
                    result = subprocess.run(
                        [script_path, file, destination_folder],
                        capture_output=True, text=True, check=True
                    )
                    processed_count += 1
                    self.logger.debug(f"Successfully processed: {basename}")
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to process {basename}: {e}")
                    self.logger.error(f"Error output: {e.stderr}")
                    continue

            self.logger.info(
                f"Photo processing completed: {processed_count} processed, {skipped_count} skipped"
            )

        except Exception as e:
            self.logger.error(f"Error processing photos: {e}")
