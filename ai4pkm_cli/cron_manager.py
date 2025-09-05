"""Cron job management system."""

import json
import os
import time
from datetime import datetime
from croniter import croniter


class CronManager:
    """Manages cron jobs defined in cron.json."""
    
    def __init__(self, logger, cloud_runner):
        """Initialize cron manager."""
        self.logger = logger
        self.claude_runner = cloud_runner
        self.jobs = []
        self.running = False
        self.thread = None
        self._load_jobs()
        
    def _load_jobs(self):
        """Load cron jobs from cron.json."""
        cron_file = "cron.json"
        if not os.path.exists(cron_file):
            self.logger.info("No cron.json found. Create one to add cron jobs.")
            return
            
        try:
            with open(cron_file, 'r') as f:
                self.jobs = json.load(f)
            self.logger.info(f"Loaded {len(self.jobs)} cron jobs from {cron_file}")
        except Exception as e:
            self.logger.error(f"Failed to load cron jobs: {e}")
            self.jobs = []
            
    def get_jobs(self):
        """Get list of loaded cron jobs."""
        return self.jobs
        
    def start(self):
        """Start the cron job scheduler."""
        if self.running:
            return
            
        self.running = True
        self.logger.info("Starting cron job scheduler")
        
        while self.running:
            try:
                self._check_and_run_jobs()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in cron scheduler: {e}")
                time.sleep(60)
                
    def stop(self):
        """Stop the cron job scheduler."""
        self.running = False
        self.logger.info("Stopping cron job scheduler")
        
    def _check_and_run_jobs(self):
        """Check if any jobs should run and execute them."""
        now = datetime.now()

        for job in self.jobs:
            try:
                inline_prompt = job.get('inline_prompt')
                cron_expr = job.get('cron')

                if not inline_prompt or not cron_expr:
                    self.logger.error(f"Invalid job configuration: {job}")
                    continue
                    
                # Check if job should run now 
                cron = croniter(cron_expr, now)
                prev_run = cron.get_prev(datetime)

                # If the previous run time is within the last minute, run the job
                time_diff = (now - prev_run).total_seconds()
                if 0 <= time_diff < 60:
                  self._run_job_inline_prompt(inline_prompt)
                
            except Exception as e:
                self.logger.error(f"Error checking job {job}: {e}")

    def _run_job_inline_prompt(self, inline_prompt):
      """Run a single inline prompt for a cron job."""
      self.logger.info(f"Running cron job inline prompt: {inline_prompt}")
      
      session_id = None
                 
      try:
          # Run the prompt using Claude
          result, session_id = self.claude_runner.run_prompt(inline_prompt=inline_prompt, session_id=session_id)
          if result:
              self.logger.info(f"Prompt completed successfully")
          else:
              self.logger.error(f"Prompt failed")
      except Exception as e:
          self.logger.error(f"Error running prompt: {e}")
