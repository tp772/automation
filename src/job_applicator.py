"""
Job Applicator Module
Handles automated job applications
"""

import requests
import time
import logging
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobApplicator:
    """Handles automated job applications"""
    
    def __init__(self, config: Dict):
        """Initialize applicator with user configuration"""
        self.config = config
        self.applied_jobs = []
        self.failed_applications = []
        
    def apply_to_job(self, job: Dict, resume_path: str, cover_letter_path: str = None) -> bool:
        """
        Apply to a single job listing
        
        Args:
            job: Job listing dictionary
            resume_path: Path to resume file
            cover_letter_path: Path to cover letter file (optional)
            
        Returns:
            True if application successful, False otherwise
        """
        try:
            source = job.get('source', 'Unknown')
            
            if source == 'Indeed':
                return self._apply_indeed(job, resume_path, cover_letter_path)
            elif source == 'Glassdoor':
                return self._apply_glassdoor(job, resume_path, cover_letter_path)
            else:
                logger.warning(f"Unknown job source: {source}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying to job {job.get('title')}: {e}")
            self.failed_applications.append({
                'job': job,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def _apply_indeed(self, job: Dict, resume_path: str, cover_letter_path: str = None) -> bool:
        """Apply to Indeed job"""
        driver = None
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
            
            driver.get(job['url'])
            
            # Wait for page to load
            time.sleep(2)
            
            # Look for apply button
            try:
                apply_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "applyButtonContainer"))
                )
                apply_button.click()
                
                # Wait for application modal
                time.sleep(2)
                
                # Check if resume upload is needed
                file_input = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                if file_input:
                    file_input[0].send_keys(resume_path)
                    logger.info(f"Uploaded resume to {job['title']} at {job['company']}")
                
                # Click submit
                submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_button.click()
                
                time.sleep(2)
                
                logger.info(f"Successfully applied to {job['title']} at {job['company']}")
                self.applied_jobs.append({
                    'job': job,
                    'timestamp': datetime.now().isoformat()
                })
                return True
                
            except Exception as e:
                logger.warning(f"Could not find apply button for Indeed job: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying to Indeed job: {e}")
            return False
        finally:
            if driver:
                driver.quit()
    
    def _apply_glassdoor(self, job: Dict, resume_path: str, cover_letter_path: str = None) -> bool:
        """Apply to Glassdoor job"""
        driver = None
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
            
            driver.get(job['url'])
            
            # Wait for page to load
            time.sleep(3)
            
            # Look for apply button
            try:
                apply_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='applyButton']"))
                )
                apply_button.click()
                
                time.sleep(2)
                
                # Handle file upload if present
                file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                if file_inputs:
                    for file_input in file_inputs:
                        try:
                            file_input.send_keys(resume_path)
                        except:
                            pass
                
                # Try to submit application
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, "button[data-test='submitApplication']")
                    submit_button.click()
                except:
                    # Alternative submit selector
                    submit_buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in submit_buttons:
                        if 'submit' in btn.text.lower() or 'apply' in btn.text.lower():
                            btn.click()
                            break
                
                time.sleep(2)
                
                logger.info(f"Successfully applied to {job['title']} at {job['company']}")
                self.applied_jobs.append({
                    'job': job,
                    'timestamp': datetime.now().isoformat()
                })
                return True
                
            except Exception as e:
                logger.warning(f"Could not complete Glassdoor application: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying to Glassdoor job: {e}")
            return False
        finally:
            if driver:
                driver.quit()
    
    def batch_apply(self, jobs: List[Dict], resume_path: str, cover_letter_path: str = None, 
                   max_applications: int = None, delay: int = 2) -> Dict:
        """
        Apply to multiple jobs
        
        Args:
            jobs: List of job listings
            resume_path: Path to resume file
            cover_letter_path: Path to cover letter file
            max_applications: Maximum number of applications to submit
            delay: Delay between applications in seconds
            
        Returns:
            Dictionary with application results
        """
        logger.info(f"Starting batch application to {len(jobs)} jobs")
        
        applied_count = 0
        for i, job in enumerate(jobs):
            if max_applications and applied_count >= max_applications:
                logger.info(f"Reached maximum applications limit: {max_applications}")
                break
            
            logger.info(f"Applying to job {i+1}/{len(jobs)}: {job.get('title')} at {job.get('company')}")
            
            if self.apply_to_job(job, resume_path, cover_letter_path):
                applied_count += 1
            
            # Add delay between applications
            if i < len(jobs) - 1:
                time.sleep(delay)
        
        return {
            'total_jobs': len(jobs),
            'successful_applications': applied_count,
            'failed_applications': len(self.failed_applications),
            'applied_jobs': self.applied_jobs,
            'failed_jobs': self.failed_applications
        }
    
    def get_application_summary(self) -> Dict:
        """Get summary of applications"""
        return {
            'total_applied': len(self.applied_jobs),
            'total_failed': len(self.failed_applications),
            'success_rate': len(self.applied_jobs) / (len(self.applied_jobs) + len(self.failed_applications)) 
                           if (len(self.applied_jobs) + len(self.failed_applications)) > 0 else 0
        }
