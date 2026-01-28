"""
Main Application Module
Orchestrates the job scraping and application automation workflow
"""

import sys
import os
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config_manager import ConfigManager
from job_scraper import JobScraper
from job_applicator import JobApplicator
from resume_handler import ResumeHandler
from database_manager import DatabaseManager

# Setup logging
def setup_logging(config: Dict):
    """Setup application logging"""
    log_dir = Path(config.get('logging', {}).get('log_file', 'logs/automation.log')).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_level = config.get('logging', {}).get('level', 'INFO')
    log_file = config.get('logging', {}).get('log_file', 'logs/automation.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


class JobAutomationApp:
    """Main job automation application"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize the job automation application
        
        Args:
            config_path: Path to configuration file
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_all_config()
        
        self.logger = setup_logging(self.config)
        self.logger.info("Initializing Job Automation Application")
        
        # Initialize components
        self.scraper = JobScraper(self.config)
        self.applicator = JobApplicator(self.config)
        self.resume_handler = ResumeHandler(self.config['resume']['base_resume_path'])
        self.db_manager = DatabaseManager(self.config['database']['path'])
    
    def scrape_jobs(self) -> List[Dict]:
        """
        Scrape jobs from configured sources
        
        Returns:
            List of job listings
        """
        self.logger.info("Starting job scraping process")
        
        keywords = self.config['job_search']['keywords']
        locations = self.config['job_search']['locations']
        
        all_jobs = []
        
        for location in locations:
            self.logger.info(f"Scraping jobs for location: {location}")
            jobs = self.scraper.scrape_all_sources(keywords, location)
            all_jobs.extend(jobs)
        
        self.logger.info(f"Total jobs scraped: {len(all_jobs)}")
        return all_jobs
    
    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Filter jobs based on configured filters
        
        Args:
            jobs: List of job listings
            
        Returns:
            Filtered list of job listings
        """
        filters = self.config['filters']
        filtered_jobs = []
        
        exclude_keywords = filters.get('exclude_keywords', [])
        required_keywords = filters.get('required_keywords', [])
        min_salary = filters.get('min_salary', 0)
        exclude_companies = filters.get('exclude_companies', [])
        
        for job in jobs:
            # Check excluded keywords
            job_text = (job.get('title', '') + ' ' + job.get('company', '')).lower()
            
            if any(keyword.lower() in job_text for keyword in exclude_keywords):
                self.logger.debug(f"Excluding job due to excluded keyword: {job.get('title')}")
                continue
            
            # Check required keywords
            if required_keywords:
                if not any(keyword.lower() in job_text for keyword in required_keywords):
                    self.logger.debug(f"Excluding job due to missing required keyword: {job.get('title')}")
                    continue
            
            # Check company exclusion list
            if job.get('company') in exclude_companies:
                self.logger.debug(f"Excluding job from excluded company: {job.get('company')}")
                continue
            
            filtered_jobs.append(job)
        
        self.logger.info(f"Jobs after filtering: {len(filtered_jobs)} (from {len(jobs)})")
        return filtered_jobs
    
    def save_jobs_to_database(self, jobs: List[Dict]):
        """
        Save jobs to database
        
        Args:
            jobs: List of job listings
        """
        for job in jobs:
            self.db_manager.add_job(job)
    
    def apply_to_jobs(self, jobs: List[Dict], max_applications: int = None) -> Dict:
        """
        Apply to filtered jobs
        
        Args:
            jobs: List of job listings to apply to
            max_applications: Maximum number of applications
            
        Returns:
            Application results
        """
        if not jobs:
            self.logger.warning("No jobs to apply to")
            return {}
        
        self.logger.info(f"Starting application process for {len(jobs)} jobs")
        
        resume_path = self.config['resume']['base_resume_path']
        
        results = self.applicator.batch_apply(
            jobs,
            resume_path,
            max_applications=max_applications,
            delay=self.config['application_settings']['delay_between_applications']
        )
        
        # Save application records to database
        for applied_job in results.get('applied_jobs', []):
            job_data = applied_job['job']
            job_id = self.db_manager.add_job(job_data)
            if job_id:
                self.db_manager.add_application(job_id, resume_path, 'applied')
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get application statistics"""
        return self.db_manager.get_application_statistics()
    
    def run(self, apply: bool = True, max_applications: int = None):
        """
        Run the complete automation workflow
        
        Args:
            apply: Whether to apply to jobs automatically
            max_applications: Maximum number of applications
        """
        try:
            self.logger.info("=" * 50)
            self.logger.info("Starting Job Automation Workflow")
            self.logger.info("=" * 50)
            
            # Step 1: Scrape jobs
            self.logger.info("\n[Step 1] Scraping jobs...")
            jobs = self.scrape_jobs()
            
            # Step 2: Save scraped jobs
            self.logger.info("\n[Step 2] Saving jobs to database...")
            self.save_jobs_to_database(jobs)
            
            # Step 3: Filter jobs
            self.logger.info("\n[Step 3] Filtering jobs...")
            filtered_jobs = self.filter_jobs(jobs)
            
            # Step 4: Apply to jobs (if enabled)
            if apply:
                self.logger.info("\n[Step 4] Applying to jobs...")
                results = self.apply_to_jobs(filtered_jobs, max_applications)
                
                self.logger.info(f"\nApplication Results:")
                self.logger.info(f"  Total jobs: {results.get('total_jobs')}")
                self.logger.info(f"  Successful applications: {results.get('successful_applications')}")
                self.logger.info(f"  Failed applications: {results.get('failed_applications')}")
            
            # Step 5: Print statistics
            self.logger.info("\n[Step 5] Application Statistics:")
            stats = self.get_statistics()
            self.logger.info(f"  Total jobs in database: {stats.get('total_jobs')}")
            self.logger.info(f"  Total applications: {stats.get('total_applied')}")
            
            status_breakdown = stats.get('status_breakdown', {})
            for status, count in status_breakdown.items():
                self.logger.info(f"  - {status}: {count}")
            
            self.logger.info("\n" + "=" * 50)
            self.logger.info("Workflow completed successfully")
            self.logger.info("=" * 50)
            
        except Exception as e:
            self.logger.error(f"Error running automation workflow: {e}", exc_info=True)
            raise


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Job Application Automation Tool')
    parser.add_argument('--config', default='config/config.json', help='Path to configuration file')
    parser.add_argument('--no-apply', action='store_true', help='Only scrape jobs, do not apply')
    parser.add_argument('--max-apply', type=int, help='Maximum number of applications to submit')
    parser.add_argument('--test', action='store_true', help='Run in test mode (dry run)')
    
    args = parser.parse_args()
    
    # Initialize and run application
    app = JobAutomationApp(args.config)
    
    apply = not args.no_apply
    max_applications = args.max_apply
    
    if args.test:
        print("Running in TEST MODE - No actual applications will be submitted")
        apply = False
    
    app.run(apply=apply, max_applications=max_applications)


if __name__ == '__main__':
    main()
