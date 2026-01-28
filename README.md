# Job Application Automation Tool

A comprehensive Python application that automates the job search and application process by scraping job listings from multiple job boards and submitting applications automatically.

## Features

- **Job Scraping**: Scrape job listings from Indeed and Glassdoor
- **Smart Filtering**: Filter jobs based on keywords, location, salary, and company preferences
- **Automated Applications**: Submit job applications automatically with customized resumes
- **Resume Management**: Customize resumes for each job application
- **Database Tracking**: Store and track all applications in SQLite database
- **Statistics**: Generate application statistics and track application status
- **Logging**: Comprehensive logging of all activities

## Project Structure

```
job-automation/
├── main.py                      # Main application entry point
├── config/
│   └── config.json             # Configuration file
├── src/
│   ├── config_manager.py       # Configuration management
│   ├── job_scraper.py          # Job scraping module
│   ├── job_applicator.py       # Automated application submission
│   ├── resume_handler.py       # Resume management and customization
│   └── database_manager.py     # Database operations
├── data/
│   └── jobs.db                 # SQLite database
├── logs/
│   └── automation.log          # Application logs
└── requirements.txt            # Python dependencies
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Chrome/Chromium browser (for Selenium automation)
- ChromeDriver (automatic with selenium)

### Setup Steps

1. Clone or download the project:
```bash
cd job-automation
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your settings:
   - Edit `config/config.json` with your preferences:
     - Job search keywords and locations
     - Resume path
     - Job filters
     - Application settings

4. Prepare your resume:
   - Place your resume file in the `resumes/` directory
   - Update the `base_resume_path` in config.json

## Configuration

Edit `config/config.json` to customize:

### Job Search Settings
```json
"job_search": {
    "keywords": ["python developer", "software engineer"],
    "locations": ["Remote", "New York, NY"],
    "job_sources": ["indeed", "glassdoor"],
    "pages_to_scrape": 5
}
```

### Application Settings
```json
"application_settings": {
    "auto_apply": true,
    "max_applications_per_day": 20,
    "delay_between_applications": 3
}
```

### Filters
```json
"filters": {
    "exclude_keywords": ["contract", "temporary"],
    "required_keywords": ["python", "rest api"],
    "min_salary": 80000,
    "exclude_companies": ["Company X"]
}
```

## Usage

### Basic Usage (Scrape and Apply)
```bash
python main.py
```

### Scrape Only (No Applications)
```bash
python main.py --no-apply
```

### Test Mode (Dry Run)
```bash
python main.py --test
```

### Limit Applications
```bash
python main.py --max-apply 10
```

### Custom Config File
```bash
python main.py --config path/to/config.json
```

## Module Documentation

### JobScraper (`src/job_scraper.py`)
Handles job scraping from various sources:
- `scrape_indeed()`: Scrape Indeed.com
- `scrape_glassdoor()`: Scrape Glassdoor.com
- `scrape_all_sources()`: Scrape all configured sources

### JobApplicator (`src/job_applicator.py`)
Handles automated job applications:
- `apply_to_job()`: Apply to a single job
- `batch_apply()`: Apply to multiple jobs
- `get_application_summary()`: Get application statistics

### ResumeHandler (`src/resume_handler.py`)
Manages resume operations:
- `load_resume()`: Load resume from file
- `customize_resume()`: Customize for specific job
- `save_resume_version()`: Save customized version
- `extract_keywords()`: Extract keywords from job description

### DatabaseManager (`src/database_manager.py`)
Database operations:
- `add_job()`: Add job to database
- `add_application()`: Record application
- `update_application_status()`: Update status
- `get_application_statistics()`: Get statistics

### ConfigManager (`src/config_manager.py`)
Configuration management:
- `load_config()`: Load configuration
- `save_config()`: Save configuration
- `get()`: Get configuration value
- `set()`: Set configuration value

## Database Schema

### Jobs Table
Stores all scraped job listings with source information

### Applications Table
Tracks submitted applications with status

### Application History Table
Maintains history of application events and updates

## Application Statuses
- `pending`: Application submitted
- `applied`: Successfully applied
- `rejected`: Application rejected
- `interviewed`: Interview scheduled
- `offered`: Job offer received

## Tips for Success

1. **Start Small**: Use `--max-apply 5` to test before full automation
2. **Monitor Logs**: Check `logs/automation.log` for details
3. **Customize Resume**: Enable resume customization in config
4. **Set Delays**: Use appropriate delays between applications (3-5 seconds)
5. **Regular Backups**: Backup your database and resume files
6. **Update Filters**: Adjust filters based on application results

## Troubleshooting

### Chrome Driver Issues
```bash
# Selenium automatically downloads ChromeDriver
# If issues persist, install webdriver-manager:
pip install webdriver-manager
```

### Connection Errors
- Check internet connection
- Verify job websites are accessible
- Try running in test mode first

### Application Failures
- Verify resume file path in config
- Check logs for specific error messages
- Try manual application first to ensure credentials work

## Important Notes

⚠️ **Terms of Service**: 
- Respect website terms of service
- Use appropriate delays between requests
- Some websites may block automated access

⚠️ **LinkedIn**:
- LinkedIn has strict anti-scraping policies
- Consider using LinkedIn API instead
- LinkedIn scraping is disabled by default

## Future Enhancements

- [ ] Support for more job boards (LinkedIn, ZipRecruiter, etc.)
- [ ] Email notification on application success
- [ ] Job description analysis and keyword matching
- [ ] Proxy support for large-scale scraping
- [ ] Web UI dashboard for monitoring
- [ ] Machine learning for job matching
- [ ] Interview preparation suggestions

## Requirements

See `requirements.txt` for all dependencies:
- beautifulsoup4: HTML parsing
- selenium: Browser automation
- requests: HTTP requests
- python-docx: Word document handling

## License

This project is provided as-is for personal use.

## Support

For issues or questions:
1. Check the logs in `logs/automation.log`
2. Review the configuration in `config/config.json`
3. Test with `--test` flag for debugging

## Disclaimer

This tool is provided for educational and personal use. Users are responsible for:
- Complying with website terms of service
- Respecting website scraping policies
- Not using this tool for spam or harassment
- Verifying applications before submission
