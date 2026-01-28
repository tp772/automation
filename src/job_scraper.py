"""
Job Scraper Module
Handles scraping job listings from various job boards
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from typing import List, Dict
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobScraper:
    """Base class for scraping job listings"""
    
    def __init__(self, config: Dict):
        """Initialize scraper with configuration"""
        self.config = config
        self.jobs = []
        self.session = requests.Session()
        
    def scrape_indeed(self, keywords: List[str], location: str, pages: int = 5) -> List[Dict]:
        """
        Scrape jobs from Indeed.com
        
        Args:
            keywords: List of job search keywords
            location: Job location
            pages: Number of pages to scrape
            
        Returns:
            List of job listings
        """
        jobs = []
        try:
            for keyword in keywords:
                for page in range(pages):
                    url = f"https://www.indeed.com/jobs?q={keyword}&l={location}&start={page*10}"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    response = self.session.get(url, headers=headers)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    job_cards = soup.find_all('div', class_='job_seen_beacon')
                    
                    for job_card in job_cards:
                        try:
                            title = job_card.find('h2', class_='jobTitle').text.strip()
                            company = job_card.find('span', class_='companyName').text.strip()
                            location_elem = job_card.find('div', class_='companyLocation')
                            location_text = location_elem.text.strip() if location_elem else "N/A"
                            
                            job_url = job_card.find('a')['href']
                            if not job_url.startswith('http'):
                                job_url = f"https://www.indeed.com{job_url}"
                            
                            job_data = {
                                'title': title,
                                'company': company,
                                'location': location_text,
                                'url': job_url,
                                'source': 'Indeed',
                                'scraped_date': datetime.now().isoformat(),
                                'keyword': keyword
                            }
                            jobs.append(job_data)
                            logger.info(f"Found job: {title} at {company}")
                        except Exception as e:
                            logger.warning(f"Error parsing job card: {e}")
                            continue
                            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
            
        return jobs
    
    def scrape_linkedin(self, keywords: List[str], location: str) -> List[Dict]:
        """
        Scrape jobs from LinkedIn
        Note: LinkedIn has strict scraping policies. Consider using LinkedIn API instead.
        
        Args:
            keywords: List of job search keywords
            location: Job location
            
        Returns:
            List of job listings
        """
        logger.warning("LinkedIn scraping requires authentication and may violate ToS. Use LinkedIn API instead.")
        return []
    
    def scrape_glassdoor(self, keywords: List[str], location: str, pages: int = 3) -> List[Dict]:
        """
        Scrape jobs from Glassdoor using Selenium for JavaScript-heavy content
        
        Args:
            keywords: List of job search keywords
            location: Job location
            pages: Number of pages to scrape
            
        Returns:
            List of job listings
        """
        jobs = []
        driver = None
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(options=options)
            
            for keyword in keywords:
                for page in range(1, pages + 1):
                    url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword}&locId={location}&includeNoSalaryJobs=true&pageNum={page}"
                    
                    try:
                        driver.get(url)
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "JobCard_jobCardContainer"))
                        )
                        
                        job_cards = driver.find_elements(By.CLASS_NAME, "JobCard_jobCardContainer")
                        
                        for job_card in job_cards:
                            try:
                                title = job_card.find_element(By.CLASS_NAME, "JobCard_jobTitle").text
                                company = job_card.find_element(By.CLASS_NAME, "EmployerProfile_companyName").text
                                location_elem = job_card.find_element(By.CLASS_NAME, "JobCard_location")
                                location_text = location_elem.text
                                
                                job_link = job_card.find_element(By.TAG_NAME, "a")
                                job_url = job_link.get_attribute("href")
                                
                                job_data = {
                                    'title': title,
                                    'company': company,
                                    'location': location_text,
                                    'url': job_url,
                                    'source': 'Glassdoor',
                                    'scraped_date': datetime.now().isoformat(),
                                    'keyword': keyword
                                }
                                jobs.append(job_data)
                                logger.info(f"Found job: {title} at {company}")
                            except Exception as e:
                                logger.warning(f"Error parsing Glassdoor job: {e}")
                                continue
                    except Exception as e:
                        logger.warning(f"Error loading Glassdoor page: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error setting up Glassdoor scraper: {e}")
        finally:
            if driver:
                driver.quit()
                
        return jobs
    
    def scrape_all_sources(self, keywords: List[str], location: str) -> List[Dict]:
        """
        Scrape from all configured job sources
        
        Args:
            keywords: List of job search keywords
            location: Job location
            
        Returns:
            Combined list of job listings from all sources
        """
        all_jobs = []
        
        logger.info(f"Starting job scrape for keywords: {keywords} in {location}")
        
        # Scrape Indeed
        indeed_jobs = self.scrape_indeed(keywords, location)
        all_jobs.extend(indeed_jobs)
        logger.info(f"Scraped {len(indeed_jobs)} jobs from Indeed")
        
        # Scrape Glassdoor
        glassdoor_jobs = self.scrape_glassdoor(keywords, location)
        all_jobs.extend(glassdoor_jobs)
        logger.info(f"Scraped {len(glassdoor_jobs)} jobs from Glassdoor")
        
        logger.info(f"Total jobs found: {len(all_jobs)}")
        return all_jobs
    
    def save_jobs(self, jobs: List[Dict], filename: str = "jobs.json"):
        """
        Save scraped jobs to JSON file
        
        Args:
            jobs: List of job listings
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(jobs)} jobs to {filename}")
        except Exception as e:
            logger.error(f"Error saving jobs: {e}")
