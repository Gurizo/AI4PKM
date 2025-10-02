# 최종 파일 경로: ai4pkm_cli/commands/sync_limitless_command.py

import os
import sys
import requests
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import time
import pytz
from tzlocal import get_localzone
from dotenv import load_dotenv

from ai4pkm_cli.config import Config

class SyncLimitlessCommand:
    def __init__(self, logger):
        self.logger = logger
        self.config = Config()
        
        load_dotenv()

        self.api_key = os.getenv("LIMITLESS_API_KEY")
        
        if not self.api_key:
            self.is_ready = False
            self.logger.warning("LIMITLESS_API_KEY not found in .env file. Skipping sync command.")
            return 

        self.is_ready = True
        limitless_config = self.config.get('commands_config', {}).get('limitless', {})
        self.api_base_url = limitless_config.get('api_base_url', "https://api.limitless.ai/v1")
        self.output_dir = Path(limitless_config.get('output_dir', "Ingest/Limitless"))
        self.start_days_ago = limitless_config.get('start_days_ago', 7)
        self.headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_sync(self):
        """
        Limitless 데이터 동기화를 실행하는 메인 함수.
        """
        if not hasattr(self, 'is_ready') or not self.is_ready:
            return True 
    
        self.logger.info("Starting Limitless data sync command...")
        try:
            local_timezone = get_localzone()
            timezone_name = str(local_timezone) 
            self.logger.info(f"Using local timezone: {timezone_name}")
            
            # 1. Fetch all data once
            all_lifelogs = self._fetch_all_recent_lifelogs()
            
            if all_lifelogs is None:
                self.logger.error("Failed to fetch data from Limitless API. Aborting sync.")
                return False

            if not all_lifelogs:
                self.logger.info("No recent lifelogs found. Sync complete.")
                return True

            # 2. Determine date range and process each day
            last_sync_str = self.get_last_sync_date()
            last_sync_date = datetime.strptime(last_sync_str, "%Y-%m-%d").date()
            today_date = date.today()
            
            print(f"📅 Last sync file found: {last_sync_date.strftime('%Y-%m-%d')}")
            print(f"🎯 Syncing up to today: {today_date.strftime('%Y-%m-%d')}")

            if last_sync_date > today_date:
                print("✅ Last sync date is in the future. Re-syncing today just in case.")
                self._filter_and_save_for_date(today_date.strftime("%Y-%m-%d"), all_lifelogs, timezone_name)
                print("\n🎉 Sync process completed.")
                self.logger.info("Limitless data sync command finished successfully.")
                return True

            dates_to_sync = self.get_date_range(last_sync_date, today_date)
            
            if not dates_to_sync:
                print("✅ Already up to date! Re-syncing today for good measure.")
                self._filter_and_save_for_date(today_date.strftime("%Y-%m-%d"), all_lifelogs, timezone_name)
            else:
                print(f"🔄 Syncing {len(dates_to_sync)} day(s): from {dates_to_sync[0]} to {dates_to_sync[-1]}")
                for date_str in dates_to_sync:
                    self._filter_and_save_for_date(date_str, all_lifelogs, timezone_name)

            print("\n🎉 Sync process completed.")
            self.logger.info("Limitless data sync command finished successfully.")
            return True
        except Exception as e:
            self.logger.error(f"An error occurred during Limitless sync command: {e}")
            return False
    
    def _fetch_all_recent_lifelogs(self):
        """
        Fetches all recent lifelogs from the API, handling pagination.
        """
        all_recent_lifelogs = []
        cursor = None
        page_count = 1
        
        print("ℹ️  Fetching all recent lifelogs from Limitless...")
        while True:
            url = f"{self.api_base_url}/lifelogs"
            params = {"limit": 10}
            if cursor:
                params['cursor'] = cursor

            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                lifelogs_page = data.get('data', {}).get('lifelogs', [])
                if not lifelogs_page:
                    print("✅ No more pages to fetch.")
                    break
                
                all_recent_lifelogs.extend(lifelogs_page)
                print(f"  - Fetched page {page_count}, {len(lifelogs_page)} entries. Total: {len(all_recent_lifelogs)}")

                cursor = data.get('meta', {}).get('lifelogs', {}).get('nextCursor')
                if not cursor or page_count > 10: # Safety break after 10 pages (~100 entries)
                    print("✅ Reached page limit or end of data.")
                    break
                
                page_count += 1
                time.sleep(0.5) # Be nice to the API

            except requests.exceptions.RequestException as e:
                print(f"⚠️ API request failed: {e}")
                if hasattr(e.response, 'text'):
                    print(f"Response: {e.response.text}")
                print("⚠️  Will proceed with the data fetched so far.")
                return all_recent_lifelogs # Return partial data instead of None
        
        print(f"✅ Retrieved {len(all_recent_lifelogs)} total entries.")
        return all_recent_lifelogs

    def _filter_and_save_for_date(self, date_str, all_lifelogs, timezone_str):
        """
        Filters a list of lifelogs for a specific date, formats, and saves them.
        """
        print(f"\n📥 Processing {date_str}...")
        target_date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        local_tz = pytz.timezone(timezone_str)
        
        filtered_lifelogs = []
        for log in all_lifelogs:
            start_time_utc_str = log.get('startTime')
            if not start_time_utc_str:
                continue
            
            utc_dt = datetime.fromisoformat(start_time_utc_str.replace('Z', '+00:00'))
            local_dt = utc_dt.astimezone(local_tz)
            
            if local_dt.date() == target_date_obj:
                filtered_lifelogs.append(log)
        
        if not filtered_lifelogs:
            print(f"ℹ️ No data found for {date_str}. Skipping file creation.")
            return

        print(f"✅ Found {len(filtered_lifelogs)} entries matching the date {date_str}.")
        
        markdown = self.format_lifelogs_markdown(filtered_lifelogs, timezone_str)
        
        if not markdown.strip():
            print(f"ℹ️ No content to save for {date_str}. Skipping file creation.")
            return

        self.save_to_file(markdown, date_str)

    def format_lifelogs_markdown(self, lifelogs, timezone_str):
        """
        Converts lifelog data to the exact markdown format used by the Obsidian plugin.
        """
        if not lifelogs:
            return "# Limitless Data\n\nNo lifelog data available for this date.\n"
        
        local_tz = pytz.timezone(timezone_str)
        
        markdown_content = ""

        for entry in sorted(lifelogs, key=lambda x: x.get('startTime', '')):
            contents = entry.get('contents', [])
            if not contents:
                continue

            for item in contents:
                item_type = item.get('type')
                content = item.get('content', '').strip()
                speaker = item.get('speakerName', 'Unknown')
                timestamp_utc_str = item.get('startTime')

                if not content:
                    continue

                if item_type == 'heading1':
                    markdown_content += f"# {content}\n"
                elif item_type == 'heading2':
                    markdown_content += f"## {content}\n"
                elif item_type == 'blockquote':
                    time_display = ""
                    if timestamp_utc_str:
                        try:
                            utc_dt = datetime.fromisoformat(timestamp_utc_str.replace('Z', '+00:00'))
                            local_dt = utc_dt.astimezone(local_tz)
                            # 플러그인 형식: "9/10/25 7:40 PM"
                            time_display = local_dt.strftime("%-m/%-d/%y %-I:%M %p")
                        except (ValueError, TypeError):
                            pass
                    
                    # 최종 출력 형식: "- Unknown (9/10/25 7:40 PM): 내용"
                    markdown_content += f"- {speaker} ({time_display}): {content}\n"
        
        return markdown_content.strip()

    def save_to_file(self, content, date_str):
        filepath = self.output_dir / f"{date_str}.md"
        try:
            filepath.write_text(content, encoding='utf-8')
            print(f"📝 Saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Failed to save file: {e}")
            return None
            
    def get_last_sync_date(self) -> str:
        """
        Finds the most recent date from the filenames in the output directory,
        mimicking the Obsidian plugin's behavior.
        """
        try:
            # YYYY-MM-DD.md 패턴에 맞는 파일찾기
            files = list(self.output_dir.glob("????-??-??.md"))
            if not files:
                # 파일이 하나도 없으면 7일 전부터 시작
                print("ℹ️ No previous sync files found. Starting from 7 days ago.")
                return (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")

            # 파일 이름("YYYY-MM-DD")에서 가장 최신 날짜를 찾기
            latest_date_str = max(file.stem for file in files)
            return latest_date_str
                
        except Exception as e:
            print(f"⚠️  Error finding last sync date from files: {e}")
            return (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        
    def get_date_range(self, start_dt, end_dt):
        dates = []
        current_dt = start_dt
        while current_dt <= end_dt:
            dates.append(current_dt.strftime("%Y-%m-%d"))
            current_dt += timedelta(days=1)
        return dates