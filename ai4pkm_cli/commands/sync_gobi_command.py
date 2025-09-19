# 최종 파일 경로: ai4pkm_cli/commands/sync_Gobi_command.py

import os
import requests
from datetime import datetime
from pathlib import Path
import pytz
from tzlocal import get_localzone

from ai4pkm_cli.config import Config


class SyncGobiCommand:
    def __init__(self, logger):
        self.logger = logger
        self.config = Config()
        self.api_key = os.getenv("GOBI_API_KEY")
        gobi_config = self.config.get("gobi_sync", {})
        self.api_base_url = gobi_config.get(
            "api_base_url", "https://api.joingobi.com/api"
        )
        self.output_dir = Path(gobi_config.get("output_dir", "Ingest/Gobi"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    def run_sync(self):
        """
        Gobi 데이터 동기화를 실행하는 메인 함수.
        """
        if not self.api_key:
            self.logger.warning(
                "GOBI_API_KEY not found in .env file. Skipping sync command."
            )
            return False

        self.logger.info("Starting Gobi data sync command...")
        try:
            local_timezone = get_localzone()
            timezone_name = str(local_timezone)
            self.logger.info(f"Using local timezone: {timezone_name}")

            transcriptions, frames = self.fetch_all_data()

            markdowns = self.format_data_markdown(transcriptions, frames, timezone_name)

            for target_date, markdown in markdowns.items():
                self.save_to_file(markdown, target_date)

            self.logger.info("Gobi data sync command finished successfully.")
            return True
        except Exception as e:
            import traceback

            traceback.print_exc()
            self.logger.error(f"An error occurred during Gobi sync command: {e}")
            return False

    def fetch_all_data(self):
        print("ℹ️  Fetching recent data...")

        last_sync_time_file = self.output_dir / "lastSyncTime.txt"
        if last_sync_time_file.exists():
            with open(last_sync_time_file, "r") as f:
                last_sync_time = int(f.read())
                last_sync_time = int(
                    datetime.fromtimestamp(last_sync_time / 1000)
                    .replace(hour=0, minute=0, second=0, microsecond=0)
                    .timestamp()
                    * 1000
                )
        else:
            last_sync_time = None

        if last_sync_time:
            params = {"lastSyncTime": last_sync_time}
        else:
            params = {}

        transcriptions = []
        frames = []
        try:
            response = requests.get(
                f"{self.api_base_url}/sync",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            transcription_chunks = data.get("transcriptions", [])
            for transcription in transcription_chunks:
                for line in transcription["transcription"].split("\n"):
                    if not line:
                        continue
                    date_time_str = ":".join(line.split(":")[:-1])
                    date_time_str = date_time_str[:23] + "Z"
                    transcriptions.append(
                        {
                            **transcription,
                            "transcription": line.split(": ")[-1],
                            "created_at": date_time_str,
                        }
                    )
            frames.extend(data.get("frames", []))
            lastSyncTime = data.get("lastSyncTime")
            with open(self.output_dir / "lastSyncTime.txt", "w") as f:
                f.write(str(lastSyncTime))

        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            if hasattr(e.response, "text"):
                print(f"Response: {e.response.text}")
            return [], []

        print(
            f"✅ Retrieved {len(transcriptions)} transcriptions and {len(frames)} frames."
        )
        return transcriptions, frames

    def format_data_markdown(self, transcriptions, frames, timezone_str):
        """
        Converts lifelog data to the exact markdown format used by the Obsidian plugin.
        """
        data = transcriptions + frames

        local_tz = pytz.timezone(timezone_str)

        markdown_contents = {}

        for entry in sorted(data, key=lambda x: x.get("created_at", "")):
            transcription = entry.get("transcription")
            downloadUrl = entry.get("downloadUrl")
            timestamp = entry.get("created_at")
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            timestamp_ms = int(dt.timestamp() * 1000)
            local_dt = dt.astimezone(local_tz)
            if local_dt.strftime("%Y-%m-%d") not in markdown_contents:
                markdown_contents[local_dt.strftime("%Y-%m-%d")] = ""
            if transcription:
                markdown_contents[local_dt.strftime("%Y-%m-%d")] += (
                    f"{local_dt.strftime('%Y-%m-%d %H:%M:%S')} {transcription}\n"
                )
            elif downloadUrl:
                filename = f"{timestamp_ms}.jpeg"
                # Create hierarchical folder structure: frames/YYYY/mm/dd/HH
                year = local_dt.strftime("%Y")
                month = local_dt.strftime("%m")
                day = local_dt.strftime("%d")
                hour = local_dt.strftime("%H")

                frames_dir = self.output_dir / "frames" / year / month / day / hour
                frames_dir.mkdir(parents=True, exist_ok=True)

                file_path = frames_dir / filename
                relative_path = f"frames/{year}/{month}/{day}/{hour}/{filename}"

                if not file_path.exists():
                    self.logger.info(f"Downloading frame {filename}...")
                    response = requests.get(downloadUrl)
                    response.raise_for_status()
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                markdown_contents[local_dt.strftime("%Y-%m-%d")] += (
                    f"{local_dt.strftime('%Y-%m-%d %H:%M:%S')} ![frame]({relative_path})\n"
                )

        return markdown_contents

    def save_to_file(self, content, target_date):
        filepath = self.output_dir / f"{target_date}.md"
        try:
            filepath.write_text(content, encoding="utf-8")
            print(f"📝 Saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Failed to save file: {e}")
            return None
