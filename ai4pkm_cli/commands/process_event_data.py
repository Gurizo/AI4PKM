import os
import shutil
from rich.console import Console

class ProcessEventData:
    """Handles intelligent processing of raw event data."""

    def __init__(self, logger, agent):
        """Initialize the data processor."""
        self.logger = logger
        self.agent = agent
        self.console = Console()

    def process_files(self, event_name):
        """
        Scans the inbox for a given event, classifies files using AI,
        and moves them to the appropriate processed data folders.
        """
        self.console.print(f"\n[bold blue]Processing data for event: {event_name}[/bold blue]")
        
        base_path = "Events"
        event_path = os.path.join(base_path, event_name)
        inbox_path = os.path.join(event_path, "_inbox")
        processed_path = os.path.join(event_path, "processed_data")

        if not os.path.exists(inbox_path):
            self.logger.error(f"Inbox directory not found for event '{event_name}' at: {inbox_path}")
            return

        # Ensure all necessary subdirectories exist
        self._create_directories(processed_path)

        self.logger.info(f"Scanning inbox: {inbox_path}")

        files_to_process = [f for f in os.listdir(inbox_path) if os.path.isfile(os.path.join(inbox_path, f))]

        if not files_to_process:
            self.console.print("[yellow]Inbox is empty. Nothing to process.[/yellow]")
            return

        for filename in files_to_process:
            file_path = os.path.join(inbox_path, filename)
            self.console.print(f"  - Processing file: {filename}")
            
            file_type = self._get_file_type(filename)
            
            category = "other"
            is_image = False

            if file_type in [".txt", ".md", ".csv"]:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.strip():
                    category = self._classify_text_content(content)
                    self.logger.info(f"    AI text classification: '{category}'")
                else:
                    self.logger.info("    File is empty, classifying as 'other'.")

            elif file_type in [".jpg", ".jpeg", ".png", ".heic"]:
                is_image = True
                category = self._classify_image_content(file_path)
                self.logger.info(f"    AI image classification: '{category}'")

            else:
                self.logger.info(f"    File type '{file_type}' not supported for AI classification yet. Classifying as 'other'.")

            # Move the file to the categorized folder
            if is_image:
                destination_folder = os.path.join(processed_path, "images", category)
            else:
                destination_folder = os.path.join(processed_path, category)
            
            destination_path = os.path.join(destination_folder, filename)
            shutil.move(file_path, destination_path)
            self.logger.info(f"    Moved file to: {destination_path}")

        self.console.print("\n[bold green]Finished processing inbox.[/bold green]")

    def _create_directories(self, processed_path):
        """Create all necessary output directories."""
        # Text categories
        os.makedirs(os.path.join(processed_path, "conversation"), exist_ok=True)
        os.makedirs(os.path.join(processed_path, "transcription"), exist_ok=True)
        os.makedirs(os.path.join(processed_path, "feedback"), exist_ok=True)
        os.makedirs(os.path.join(processed_path, "vendor_list"), exist_ok=True)
        os.makedirs(os.path.join(processed_path, "notes"), exist_ok=True)
        
        # Image categories
        os.makedirs(os.path.join(processed_path, "images", "dance_scene"), exist_ok=True)
        os.makedirs(os.path.join(processed_path, "images", "dj_booth"), exist_ok=True)
        os.makedirs(os.path.join(processed_path, "images", "food_vendor"), exist_ok=True)
        os.makedirs(os.path.join(processed_path, "images", "game_booth"), exist_ok=True)
        os.makedirs(os.path.join(processed_path, "images", "receipt"), exist_ok=True)
        os.makedirs(os.path.join(processed_path, "images", "crowd"), exist_ok=True)
        
        # Default/Other
        os.makedirs(os.path.join(processed_path, "other"), exist_ok=True)
        os.makedirs(os.path.join(processed_path, "images", "other"), exist_ok=True)

    def _classify_text_content(self, content):
        """Uses AI to classify the content of a text file."""
        prompt = f"""
You are a file content classifier. Your task is to determine the type of content in the following text.
The possible categories are:
- 'conversation': A back-and-forth dialogue or discussion between two or more people.
- 'transcription': A chronological log of spoken words, likely from a meeting or monologue.
- 'feedback': A user's opinion, survey response, or feedback about an event.
- 'vendor_list': A list of businesses, suppliers, or vendors.
- 'notes': General notes, ideas, or unstructured text that doesn't fit other categories.

Based on the content below, respond with only one of the category names listed above.

---
CONTENT:
{content}
---
"""
        try:
            result = self.agent.run_prompt(inline_prompt=prompt)
            category = result[0].strip().lower().replace("'", "") if result and result[0] else "other"
            
            if category not in ['conversation', 'transcription', 'feedback', 'vendor_list', 'notes']:
                return "other"
            return category
        except Exception as e:
            self.logger.error(f"    AI text classification failed: {e}")
            return "other"

    def _classify_image_content(self, file_path):
        """Uses AI to classify the content of an image file."""
        prompt = f"""
Analyze the content of this event photo. Based on the main subject of the image, classify it into one of the following categories:
- 'dance_scene': One or more people are actively dancing, especially on a stage or designated performance area.
- 'dj_booth': The main subject is the DJ, their equipment, or the DJ booth.
- 'food_vendor': A food stall, truck, or booth is clearly visible.
- 'game_booth': A booth or area for a game or interactive activity is the main subject.
- 'receipt': The image is a photo or scan of a receipt or invoice.
- 'crowd': A general photo of the audience or a large group of people not specifically dancing on stage.
- 'other': The image does not fit any of the above categories.

Respond with only one of the category names listed above.

Image to analyze: {file_path}
"""
        try:
            result = self.agent.run_prompt(inline_prompt=prompt)
            category = result[0].strip().lower().replace("'", "") if result and result[0] else "other"

            valid_categories = ['dance_scene', 'dj_booth', 'food_vendor', 'game_booth', 'receipt', 'crowd']
            if category not in valid_categories:
                return "other"
            return category
        except Exception as e:
            self.logger.error(f"    AI image classification failed: {e}")
            return "other"

    def _get_file_type(self, filename):
        """Determines the file type based on its extension."""
        _, extension = os.path.splitext(filename)
        return extension.lower()