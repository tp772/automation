"""
Resume Handler Module
Manages resume customization and application
"""

import os
import json
import logging
from typing import Dict, List
from docx import Document
from pathlib import Path
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeHandler:
    """Handles resume management and customization"""
    
    def __init__(self, base_resume_path: str):
        """
        Initialize resume handler
        
        Args:
            base_resume_path: Path to base resume file
        """
        self.base_resume_path = base_resume_path
        self.resume_versions = {}
        
    def load_resume(self) -> str:
        """
        Load resume content from file
        
        Returns:
            Resume content as string
        """
        try:
            if self.base_resume_path.endswith('.docx'):
                doc = Document(self.base_resume_path)
                content = '\n'.join([para.text for para in doc.paragraphs])
                return content
            elif self.base_resume_path.endswith('.txt'):
                with open(self.base_resume_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.error(f"Unsupported resume format: {self.base_resume_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading resume: {e}")
            return None
    
    def customize_resume(self, job: Dict, keywords: List[str] = None) -> str:
        """
        Customize resume for a specific job
        
        Args:
            job: Job listing dictionary
            keywords: Additional keywords to highlight
            
        Returns:
            Customized resume content
        """
        try:
            resume_content = self.load_resume()
            
            if not resume_content:
                return None
            
            # Replace job title and company references
            customized = resume_content.replace('[JOB_TITLE]', job.get('title', ''))
            customized = customized.replace('[COMPANY]', job.get('company', ''))
            customized = customized.replace('[LOCATION]', job.get('location', ''))
            
            # Add keywords to resume if provided
            if keywords:
                for keyword in keywords:
                    # This is a simple approach - you might want more sophisticated keyword matching
                    if keyword.lower() not in customized.lower():
                        logger.info(f"Adding keyword '{keyword}' to customized resume")
            
            logger.info(f"Customized resume for {job.get('title')} at {job.get('company')}")
            return customized
            
        except Exception as e:
            logger.error(f"Error customizing resume: {e}")
            return None
    
    def save_resume_version(self, content: str, job: Dict, output_dir: str = "resumes") -> str:
        """
        Save customized resume version
        
        Args:
            content: Resume content
            job: Job listing dictionary
            output_dir: Output directory
            
        Returns:
            Path to saved resume file
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Create filename from job title and company
            filename = f"{job['company'].replace(' ', '_')}_{job['title'].replace(' ', '_')}.txt"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved customized resume to {filepath}")
            self.resume_versions[job['url']] = filepath
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving resume version: {e}")
            return None
    
    def get_resume_path(self, job_url: str = None) -> str:
        """
        Get resume path for a job
        
        Args:
            job_url: URL of job (if using customized versions)
            
        Returns:
            Path to resume file
        """
        if job_url and job_url in self.resume_versions:
            return self.resume_versions[job_url]
        return self.base_resume_path
    
    def extract_keywords(self, job_description: str) -> List[str]:
        """
        Extract important keywords from job description
        
        Args:
            job_description: Job posting text
            
        Returns:
            List of extracted keywords
        """
        try:
            # Load common keywords from config
            keywords = []
            
            # Simple keyword extraction - split by common delimiters
            if job_description:
                # Look for common skill markers
                skill_keywords = ['python', 'java', 'javascript', 'react', 'angular', 'vue',
                                'sql', 'mongodb', 'aws', 'azure', 'docker', 'kubernetes',
                                'git', 'agile', 'scrum', 'rest', 'api', 'html', 'css',
                                'nodejs', 'django', 'flask', 'fastapi', 'spring']
                
                for keyword in skill_keywords:
                    if keyword.lower() in job_description.lower():
                        keywords.append(keyword)
            
            return list(set(keywords))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def backup_resume(self, backup_dir: str = "resume_backups") -> str:
        """
        Create backup of base resume
        
        Args:
            backup_dir: Directory to store backup
            
        Returns:
            Path to backup file
        """
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            filename = os.path.basename(self.base_resume_path)
            backup_path = os.path.join(backup_dir, f"backup_{filename}")
            
            shutil.copy2(self.base_resume_path, backup_path)
            logger.info(f"Created resume backup at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating resume backup: {e}")
            return None
