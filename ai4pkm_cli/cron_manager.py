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
                prompts = job.get('prompts')
                cron_expr = job.get('cron')

                if not prompts or not cron_expr:
                    self.logger.error(f"Invalid job configuration: {job}")
                    continue
                    
                # Check if job should run now 
                cron = croniter(cron_expr, now)
                prev_run = cron.get_prev(datetime)

                # If the previous run time is within the last minute, run the job
                time_diff = (now - prev_run).total_seconds()
                if 0 <= time_diff < 60:
                    self._run_job_sequence(prompts, job.get('description', 'Unnamed job'))
                    
            except Exception as e:
                self.logger.error(f"Error checking job {job}: {e}")
                
    def _run_job_sequence(self, prompts, job_description):
        """Run a sequence of prompts for a cron job."""
        self.logger.info(f"Running cron job sequence: {job_description}")
        self.logger.info(f"Processing {len(prompts)} prompts sequentially")
        
        session_id = None
        for i, prompt_name in enumerate(prompts, 1):
            self.logger.info(f"Running prompt {i}/{len(prompts)}: {prompt_name}")
            
            # Check if prompt file exists
            prompt_file = f"_Settings_/Prompts/{prompt_name}.md"
            if not os.path.exists(prompt_file):
                self.logger.error(f"Prompt file not found: {prompt_file}")
                continue
                
            try:
                # Run the prompt using Claude
                result, session_id = self.claude_runner.run_prompt(prompt_name, session_id=session_id)
                if result:
                    self.logger.info(f"Prompt {prompt_name} completed successfully")
                else:
                    self.logger.error(f"Prompt {prompt_name} failed")
            except Exception as e:
                self.logger.error(f"Error running prompt {prompt_name}: {e}")
                
        self.logger.info(f"Completed cron job sequence: {job_description}")
    
    def _run_job(self, prompt_name):
        """Run a specific cron job (legacy method for backward compatibility)."""
        self._run_job_sequence([prompt_name], f"Single prompt: {prompt_name}")
