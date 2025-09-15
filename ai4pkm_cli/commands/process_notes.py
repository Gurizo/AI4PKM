"""Apple Notes processing system with AppleScript integration."""

import glob
import json
import os
import re
import shutil
import subprocess
from typing import Optional, Set, Dict, Any

from rich.console import Console


class ProcessNotes:
    """Handles Apple Notes processing with configurable destination folders."""

    def __init__(self, logger, config: Optional[Any] = None):
        """Initialize notes processor."""
        self.logger = logger
        self.console = Console()
        self.config = config

    def process_notes(self, use_cache: bool = False) -> None:
        """Process Apple Notes with configurable destination folder.
        
        Args:
            use_cache (bool): If True, use cached AppleScript export instead of re-running
        """
        
        # Get configurable paths and settings
        if self.config:
            destination_folder = self.config.get_notes_destination_folder()
            days = self.config.get_notes_days()
        else:
            # Use defaults if no config object provided
            destination_folder = "Ingest/Apple Notes/"
            days = 7

        self.logger.info(f"Processing notes to: {destination_folder}")
        self.logger.info(f"Looking back {days} days")
        
        # Check existing files for smarter duplicate handling
        existing_files = set()
        if os.path.exists(destination_folder):
            for filename in os.listdir(destination_folder):
                if filename.endswith('.md'):
                    # Extract the original note title from filename
                    # Format: YYYY-MM-DD Title.md -> Title
                    name_part = filename[11:-3]  # Remove date prefix and .md
                    existing_files.add(name_part)
        
        self.logger.info(f"Found {len(existing_files)} existing processed notes")

        # Create temporary directory for AppleScript exports
        temp_folder = os.path.join(destination_folder, "_temp_export")
        cache_folder = os.path.join(destination_folder, "_cache_export")
        
        # Handle caching logic
        try:
            if use_cache and os.path.exists(cache_folder) and os.listdir(cache_folder):
                self.logger.info("Using cached AppleScript export (skipping Notes app export)...")
                # Copy cache to temp folder
                if os.path.exists(temp_folder):
                    shutil.rmtree(temp_folder)
                shutil.copytree(cache_folder, temp_folder)
            else:
                # Export notes using AppleScript
                self.logger.info("Exporting notes from Apple Notes app...")
                
                # Get the script path relative to the package root
                script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "export_notes.applescript")
                script_path = os.path.abspath(script_path)
                
                if not os.path.exists(script_path):
                    self.logger.error(f"AppleScript not found: {script_path}")
                    return

                # Execute AppleScript (just export recent notes, we'll handle duplicates in Python)
                result = subprocess.run(
                    ["osascript", script_path, temp_folder, str(days)], 
                    capture_output=True, text=True, check=True
                )
                
                # Log AppleScript output
                if result.stderr:
                    for line in result.stderr.strip().split('\n'):
                        line = line.strip()
                        if line:
                            if any(keyword in line for keyword in ["Exported:", "Export completed:", "Total notes"]):
                                self.logger.info(f"AppleScript: {line}")
                            else:
                                self.logger.debug(f"AppleScript: {line}")
                                
                self.logger.info("Notes export completed successfully")
                
                # Save cache for future use (only if export was successful)
                try:
                    if os.path.exists(cache_folder):
                        shutil.rmtree(cache_folder)
                    shutil.copytree(temp_folder, cache_folder)
                    self.logger.info(f"Cached export for future use")
                except Exception as cache_error:
                    self.logger.warning(f"Could not create cache: {cache_error}")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"AppleScript execution failed: {e}")
            self.logger.error(f"Error output: {e.stderr}")
            return
        except Exception as e:
            self.logger.error(f"Error exporting/caching notes: {e}")
            return

        try:
            # Process exported files
            self.logger.info("Processing exported notes...")
            
            # Ensure destination directory exists
            os.makedirs(destination_folder, exist_ok=True)
            
            # Create _files_ directory for attachments
            files_folder = os.path.join(destination_folder, "_files_")
            os.makedirs(files_folder, exist_ok=True)
            
            # Find all JSON metadata files in temp folder
            json_pattern = os.path.join(temp_folder, "*.json")
            json_files = glob.glob(json_pattern)
            
            self.logger.debug(f"Looking for JSON files with pattern: {json_pattern}")
            self.logger.info(f"Found {len(json_files)} exported notes to process")
            
            processed_count = 0
            skipped_count = 0
            
            for json_file in json_files:
                try:
                    # Load metadata
                    with open(json_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Get corresponding HTML file
                    base_name = os.path.splitext(os.path.basename(json_file))[0]
                    html_file = os.path.join(temp_folder, base_name + ".html")
                    
                    if not os.path.exists(html_file):
                        self.logger.warning(f"HTML file not found for: {base_name}")
                        continue
                    
                    # Check if already processed by comparing with existing files
                    title = metadata.get('title', 'Untitled')
                    safe_title = self._sanitize_title(title)
                    
                    if safe_title in existing_files:
                        skipped_count += 1
                        self.logger.debug(f"Already processed: {title}")
                        continue
                    
                    # Process the note
                    self._process_single_note(metadata, html_file, destination_folder, files_folder)
                    processed_count += 1
                    
                    final_filename = base_name + ".md"
                    self.logger.info(f"Processed: {final_filename}")
                    
                except FileNotFoundError as e:
                    self.logger.error(f"File not found while processing {json_file}: {e}")
                    continue
                except PermissionError as e:
                    self.logger.error(f"Permission denied while processing {json_file}: {e}")
                    continue
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON in {json_file}: {e}")
                    continue
                except Exception as e:
                    self.logger.error(f"Unexpected error processing {json_file}: {e}")
                    continue
            
            self.logger.info(f"Notes processing completed: {processed_count} processed, {skipped_count} skipped")
            
        except Exception as e:
            self.logger.error(f"Error processing notes: {e}")
        finally:
            # Clean up temp folder
            try:
                if os.path.exists(temp_folder):
                    shutil.rmtree(temp_folder)
                    self.logger.debug("Cleaned up temporary export folder")
            except Exception as e:
                self.logger.warning(f"Could not clean up temp folder: {e}")

    def _sanitize_title(self, title: str) -> str:
        """Sanitize title to match the format used in filenames."""
        # Apply same sanitization as AppleScript
        safe_title = title.replace("/", "-").replace("\\", "-").replace(":", "-")
        safe_title = safe_title.replace("*", "-").replace("?", "-").replace("\"", "-")
        safe_title = safe_title.replace("<", "-").replace(">", "-").replace("|", "-")
        safe_title = safe_title.replace("  ", " ").strip()
        
        # Limit length like AppleScript
        if len(safe_title) > 100:
            safe_title = safe_title[:100]
        
        return safe_title

    def _process_single_note(self, metadata, html_file, destination_folder, files_folder):
        """Process a single note: convert to markdown and handle attachments."""
        
        # Read HTML content
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract date from filename for YYYY-MM-DD prefix
        filename = metadata.get('filename', '')
        date_match = re.match(r'^(\d{4}-\d{2}-\d{2})', filename)
        date_prefix = date_match.group(1) if date_match else metadata.get('created', '').split('T')[0]
        
        # Process attachments BEFORE converting to markdown (extract images from data URLs in HTML)
        note_title = metadata.get('title', 'Untitled')
        html_content = self._process_attachments_html(html_content, note_title, date_prefix, files_folder)
        
        # Convert HTML to markdown
        markdown_content = self._html_to_markdown(html_content)
        
        # Clean up empty image references that result from data:image removal
        markdown_content = re.sub(r'!\[\]\(\)', '', markdown_content)
        
        # Append extracted images at the end of the content
        if hasattr(self, '_extracted_images') and self._extracted_images:
            if markdown_content.strip():
                markdown_content += "\n\n---\n\n"
            markdown_content += "\n".join(self._extracted_images)
        
        # Create frontmatter
        frontmatter = self._create_frontmatter(metadata)
        
        # Combine frontmatter and content
        final_content = frontmatter + "\n\n" + markdown_content
        
        # Clean up redundant newlines
        final_content = self._clean_markdown_newlines(final_content)
        
        # Save markdown file
        final_filename = filename + ".md"
        final_path = os.path.join(destination_folder, final_filename)
        
        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

    def _html_to_markdown(self, html_content):
        """Convert HTML content to markdown."""
        try:
            # Try to use html2text if available
            import html2text
            converter = html2text.HTML2Text()
            converter.ignore_links = False
            converter.body_width = 0  # Don't wrap lines
            converter.unicode_snob = True  # Better Unicode handling
            return converter.handle(html_content).strip()
        except ImportError:
            # Fallback: basic HTML stripping
            self.logger.debug("html2text not available, using basic conversion. Install with: pip install html2text")
            return self._basic_html_to_markdown(html_content)

    def _basic_html_to_markdown(self, html_content):
        """Basic HTML to markdown conversion without external dependencies."""
        import html
        
        # Unescape HTML entities
        content = html.unescape(html_content)
        
        # Remove common empty or problematic patterns first
        content = re.sub(r'<[^>]*>\s*</[^>]*>', '', content)  # Empty tags
        content = re.sub(r'<br\s*/?>', '\n', content)
        
        # Basic tag conversions with non-empty content check
        content = re.sub(r'<p[^>]*>(.*?)</p>', lambda m: m.group(1).strip() + '\n\n' if m.group(1).strip() else '', content, flags=re.DOTALL)
        content = re.sub(r'<b[^>]*>(.*?)</b>', lambda m: f'**{m.group(1).strip()}**' if m.group(1).strip() else '', content, flags=re.DOTALL)
        content = re.sub(r'<strong[^>]*>(.*?)</strong>', lambda m: f'**{m.group(1).strip()}**' if m.group(1).strip() else '', content, flags=re.DOTALL)
        content = re.sub(r'<i[^>]*>(.*?)</i>', lambda m: f'*{m.group(1).strip()}*' if m.group(1).strip() else '', content, flags=re.DOTALL)
        content = re.sub(r'<em[^>]*>(.*?)</em>', lambda m: f'*{m.group(1).strip()}*' if m.group(1).strip() else '', content, flags=re.DOTALL)
        content = re.sub(r'<h1[^>]*>(.*?)</h1>', lambda m: f'# {m.group(1).strip()}\n\n' if m.group(1).strip() else '', content, flags=re.DOTALL)
        content = re.sub(r'<h2[^>]*>(.*?)</h2>', lambda m: f'## {m.group(1).strip()}\n\n' if m.group(1).strip() else '', content, flags=re.DOTALL)
        content = re.sub(r'<h3[^>]*>(.*?)</h3>', lambda m: f'### {m.group(1).strip()}\n\n' if m.group(1).strip() else '', content, flags=re.DOTALL)
        content = re.sub(r'<h4[^>]*>(.*?)</h4>', lambda m: f'#### {m.group(1).strip()}\n\n' if m.group(1).strip() else '', content, flags=re.DOTALL)
        content = re.sub(r'<h5[^>]*>(.*?)</h5>', lambda m: f'##### {m.group(1).strip()}\n\n' if m.group(1).strip() else '', content, flags=re.DOTALL)
        content = re.sub(r'<h6[^>]*>(.*?)</h6>', lambda m: f'###### {m.group(1).strip()}\n\n' if m.group(1).strip() else '', content, flags=re.DOTALL)
        
        # Handle lists
        content = re.sub(r'<ul[^>]*>(.*?)</ul>', lambda m: self._process_list(m.group(1), '-'), content, flags=re.DOTALL)
        content = re.sub(r'<ol[^>]*>(.*?)</ol>', lambda m: self._process_list(m.group(1), '1.'), content, flags=re.DOTALL)
        
        # Remove remaining tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove empty markdown patterns
        content = re.sub(r'\*\*\s*\*\*', '', content)  # Empty bold
        content = re.sub(r'\*\s*\*', '', content)  # Empty italic
        content = re.sub(r'^#+\s*$', '', content, flags=re.MULTILINE)  # Empty headings
        
        # Clean up excessive whitespace and newlines
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Multiple newlines -> double newline
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces/tabs -> single space
        content = re.sub(r'\n ', '\n', content)  # Remove spaces at start of lines
        content = re.sub(r' +\n', '\n', content)  # Remove trailing spaces
        
        return content.strip()

    def _process_list(self, list_content, marker):
        """Process HTML list items."""
        items = re.findall(r'<li[^>]*>(.*?)</li>', list_content, flags=re.DOTALL)
        result = []
        for i, item in enumerate(items):
            item_marker = marker if marker == '-' else f"{i+1}."
            result.append(f"{item_marker} {item.strip()}")
        return '\n'.join(result) + '\n\n'

    def _process_attachments_html(self, html_content, note_title, date_prefix, files_folder):
        """Extract images from data URLs in HTML and save them as files."""
        import base64
        import os
        
        # Sanitize note title for use in filenames
        safe_title = self._sanitize_title(note_title)
        
        # Find all data URLs in the HTML content  
        data_url_pattern = r'data:image/([^;]+);base64,([^"\'>\s]+)'
        
        image_count = 0
        extracted_images = []
        
        def extract_data_url(match):
            nonlocal image_count
            image_format = match.group(1)
            image_data = match.group(2)
            
            try:
                # Decode base64 image
                decoded_data = base64.b64decode(image_data)
                
                # Create filename with note title and date prefix
                image_count += 1
                filename = f"{date_prefix} {safe_title}-image{image_count:02d}.{image_format}"
                image_path = os.path.join(files_folder, filename)
                
                # Ensure files folder exists
                os.makedirs(files_folder, exist_ok=True)
                
                # Save image file
                with open(image_path, 'wb') as f:
                    f.write(decoded_data)
                
                # Store image info for later (using wiki-style linking)
                extracted_images.append(f"![[{filename}]]")
                
                # Remove the data URL entirely (will be added back as markdown at the end)
                return ""
                
            except Exception as e:
                self.logger.warning(f"Could not extract image: {e}")
                return ""
        
        # Remove all data URLs and extract images
        processed_content = re.sub(data_url_pattern, extract_data_url, html_content)
        
        if image_count > 0:
            self.logger.info(f"Extracted {image_count} images from HTML to _files_/")
            
            # Store the extracted images list for later use
            # We'll add them at the end of the content after HTML-to-markdown conversion
            self._extracted_images = extracted_images
        else:
            self._extracted_images = []
        
        return processed_content
    
    def _convert_image_placeholders(self, markdown_content):
        """Convert image placeholders to proper markdown syntax."""
        # Pattern to match: [EXTRACTED_IMAGE_1_AT_PATH__files_/filename.png]
        placeholder_pattern = r'\[EXTRACTED_IMAGE_(\d+)_AT_PATH_([^\]]+)\]'
        
        def replace_placeholder(match):
            image_num = match.group(1) 
            filename = match.group(2).split('/')[-1]  # Extract just the filename
            return f"![[{filename}]]"
        
        converted = re.sub(placeholder_pattern, replace_placeholder, markdown_content)
        
        num_placeholders = len(re.findall(placeholder_pattern, markdown_content))
        if num_placeholders > 0:
            self.logger.info(f"Converted {num_placeholders} image placeholders to markdown syntax")
        
        return converted

    def _process_attachments(self, markdown_content, note_title, date_prefix, files_folder):
        """Extract images from data URLs and save them as files."""
        import base64
        import os
        
        # Find all data URLs in the markdown content
        data_url_pattern = r'!\[([^\]]*)\]\(data:image/([^;]+);base64,([^)]+)\)'
        
        # Sanitize note title for filename
        safe_title = self._sanitize_title(note_title)[:50]  # Limit length
        
        image_count = 0
        def replace_data_url(match):
            nonlocal image_count
            alt_text = match.group(1)
            image_format = match.group(2) 
            image_data = match.group(3)
            
            try:
                # Decode base64 image
                decoded_data = base64.b64decode(image_data)
                
                # Create filename with date prefix and note title
                image_count += 1
                filename = f"{date_prefix} {safe_title}-image{image_count:02d}.{image_format}"
                image_path = os.path.join(files_folder, filename)
                
                # Ensure files folder exists
                os.makedirs(files_folder, exist_ok=True)
                
                # Save image file
                with open(image_path, 'wb') as f:
                    f.write(decoded_data)
                
                # Return markdown link to the saved file
                relative_path = f"_files_/{filename}"
                return f"![{alt_text}]({relative_path})"
                
            except Exception as e:
                self.logger.warning(f"Could not extract image: {e}")
                # Return original data URL if extraction fails
                return match.group(0)
        
        # Replace all data URLs with file links
        processed_content = re.sub(data_url_pattern, replace_data_url, markdown_content)
        
        if image_count > 0:
            self.logger.info(f"Extracted {image_count} images to _files_/")
        
        return processed_content

    def _create_frontmatter(self, metadata: Dict[str, Any]) -> str:
        """Create YAML frontmatter for the note."""
        title = metadata.get('title', 'Untitled')
        created = metadata.get('created', '')
        modified = metadata.get('modified', '')
        
        # Extract just the date part for frontmatter
        created_date = created.split('T')[0] if created else ''
        modified_date = modified.split('T')[0] if modified else ''
        
        frontmatter = f"""---
title: "{title}"
source: "Apple Notes"
created: {created_date}
modified: {modified_date}
tags:
  - notes
  - imported
---"""
        
        return frontmatter

    def _clean_markdown_newlines(self, content):
        """Clean up redundant newlines and whitespace in markdown content."""
        # First, remove any empty markdown patterns that might have been created (but preserve ---)
        content = re.sub(r'\*\*\s*\*\*', '', content)  # Empty bold
        content = re.sub(r'\*\s*\*(?!\*)', '', content)  # Empty italic (but not part of bold)
        content = re.sub(r'^#+\s*$', '', content, flags=re.MULTILINE)  # Empty headings
        content = re.sub(r'^>\s*$', '', content, flags=re.MULTILINE)  # Empty blockquotes
        
        # Split into lines and clean each line
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove trailing and leading whitespace
            cleaned_line = line.strip()
            # Only keep non-empty lines or preserve intentional empty lines for formatting
            cleaned_lines.append(cleaned_line)
        
        # Filter out lines that are truly empty or contain only whitespace/formatting
        final_lines = []
        in_frontmatter = False
        
        for i, line in enumerate(cleaned_lines):
            # Track if we're in frontmatter section (preserve everything there)
            if line == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    final_lines.append(line)
                    continue
                else:
                    in_frontmatter = False
                    final_lines.append(line)
                    continue
            
            # If in frontmatter, preserve all lines as-is
            if in_frontmatter:
                final_lines.append(line)
                continue
            
            # Skip lines that are empty or contain only markdown artifacts (content only)
            # But preserve frontmatter delimiters (---)
            if line == '' or (re.match(r'^[\s\*#>-]*$', line) and line != '---'):
                # Add blank line BEFORE headings (between content and next section)
                # But NOT after headings (no gap between section and content)
                # And NOT between headings (no gap between heading levels)
                prev_line = cleaned_lines[i-1] if i > 0 else ''
                next_line = cleaned_lines[i+1] if i < len(cleaned_lines) - 1 else ''
                
                prev_is_heading = prev_line.startswith('#')
                next_is_heading = next_line.startswith('#')
                
                # Only keep empty line before a heading when transitioning from content
                # NOT after headings (heading -> content) or between headings (heading -> heading)
                if not prev_is_heading and next_is_heading and prev_line != '':
                    final_lines.append('')
            else:
                final_lines.append(line)
        
        # Join and handle multiple consecutive newlines
        content = '\n'.join(final_lines)
        
        # Final aggressive newline cleanup (frontmatter is already protected)
        content = re.sub(r'\n{3,}', '\n\n', content)  # Max 2 consecutive newlines
        
        # Final cleanup
        content = content.rstrip() + '\n'  # Single trailing newline
        
        return content
