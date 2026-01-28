"""
Database Manager
Handles storing and retrieving job application data
"""

import sqlite3
import json
import logging
from typing import List, Dict
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database for job tracking"""
    
    def __init__(self, db_path: str = "data/jobs.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    url TEXT UNIQUE,
                    source TEXT,
                    job_description TEXT,
                    scraped_date TIMESTAMP,
                    is_duplicate INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create applications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    resume_path TEXT,
                    applied_date TIMESTAMP,
                    status TEXT,
                    notes TEXT,
                    follow_up_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES jobs(id)
                )
            ''')
            
            # Create application history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS application_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id INTEGER NOT NULL,
                    event TEXT,
                    event_date TIMESTAMP,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (application_id) REFERENCES applications(id)
                )
            ''')
            
            # Create filters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_filters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filter_name TEXT UNIQUE,
                    filter_criteria TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def add_job(self, job: Dict) -> int:
        """
        Add job to database
        
        Args:
            job: Job dictionary
            
        Returns:
            Job ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO jobs (title, company, location, url, source, job_description, scraped_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.get('title'),
                job.get('company'),
                job.get('location'),
                job.get('url'),
                job.get('source'),
                job.get('description', ''),
                job.get('scraped_date', datetime.now().isoformat())
            ))
            
            conn.commit()
            job_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"Added job to database: {job.get('title')} (ID: {job_id})")
            return job_id
            
        except sqlite3.IntegrityError:
            logger.warning(f"Job already exists in database: {job.get('url')}")
            return None
        except Exception as e:
            logger.error(f"Error adding job to database: {e}")
            return None
    
    def add_application(self, job_id: int, resume_path: str, status: str = "pending") -> int:
        """
        Record job application
        
        Args:
            job_id: ID of the job
            resume_path: Path to resume used
            status: Application status
            
        Returns:
            Application ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO applications (job_id, resume_path, applied_date, status)
                VALUES (?, ?, ?, ?)
            ''', (job_id, resume_path, datetime.now().isoformat(), status))
            
            conn.commit()
            app_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"Recorded application: Job ID {job_id}, Application ID {app_id}")
            return app_id
            
        except Exception as e:
            logger.error(f"Error adding application: {e}")
            return None
    
    def update_application_status(self, app_id: int, status: str, notes: str = None):
        """
        Update application status
        
        Args:
            app_id: Application ID
            status: New status (pending, applied, rejected, interviewed, offered)
            notes: Optional notes
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE applications 
                SET status = ?, notes = ?
                WHERE id = ?
            ''', (status, notes, app_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated application {app_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Error updating application status: {e}")
    
    def get_applied_jobs(self) -> List[Dict]:
        """Get list of all applied jobs"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT j.*, a.status, a.applied_date
                FROM jobs j
                JOIN applications a ON j.id = a.job_id
                ORDER BY a.applied_date DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error retrieving applied jobs: {e}")
            return []
    
    def get_jobs_by_status(self, status: str) -> List[Dict]:
        """Get jobs by application status"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT j.*, a.status, a.applied_date
                FROM jobs j
                JOIN applications a ON j.id = a.job_id
                WHERE a.status = ?
                ORDER BY a.applied_date DESC
            ''', (status,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error retrieving jobs by status: {e}")
            return []
    
    def get_application_statistics(self) -> Dict:
        """Get application statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM jobs')
            total_jobs = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM applications')
            total_applied = cursor.fetchone()[0]
            
            cursor.execute('SELECT status, COUNT(*) FROM applications GROUP BY status')
            status_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                'total_jobs': total_jobs,
                'total_applied': total_applied,
                'status_breakdown': status_breakdown
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def search_jobs(self, keyword: str, location: str = None) -> List[Dict]:
        """Search jobs in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if location:
                cursor.execute('''
                    SELECT * FROM jobs
                    WHERE (title LIKE ? OR company LIKE ?)
                    AND location LIKE ?
                ''', (f'%{keyword}%', f'%{keyword}%', f'%{location}%'))
            else:
                cursor.execute('''
                    SELECT * FROM jobs
                    WHERE title LIKE ? OR company LIKE ?
                ''', (f'%{keyword}%', f'%{keyword}%'))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return []
