# LinkedIn Profile Data Collection System

A comprehensive, production-ready LinkedIn data collection system designed for large-scale profile analysis and research. This system efficiently scrapes LinkedIn profiles, companies, job postings, and articles while maintaining strict data integrity and following best practices for web scraping.

## 🛠️ Project Overview

This LinkedIn data collection system was built to address the need for structured, reliable LinkedIn data for research, recruitment, market analysis, and competitive intelligence. Unlike generic scrapers, this system is specifically designed for:

- **Large-scale data collection** (600+ profiles in a single run)
- **Production-grade reliability** with comprehensive error handling
- **Strict data formatting** following JSONL standards for seamless integration
- **Incremental processing** to handle interruptions gracefully
- **Professional data management** with automatic file chunking and validation

## 🚀 Key Features

### **Advanced Profile Scraping**
- **Comprehensive data extraction** from LinkedIn profile pages
- **Batch processing** with configurable batch sizes (default: 10 profiles per batch)
- **Rate limiting** with intelligent delays to respect LinkedIn's servers
- **Error recovery** that continues processing even if individual profiles fail

### **Production-Ready Data Management**
- **JSONL format compliance** - Each record is a complete, valid JSON object
- **Automatic file chunking** - Splits large datasets into 100,000-record files
- **Incremental saving** - Saves data as it's scraped, preventing data loss
- **Data integrity verification** - Validates all output files before completion
- **Resume capability** - Can handle interruptions without losing progress

### **Multi-Entity Support**
- **Profile scraping** - Individual LinkedIn profiles with full metadata
- **Company pages** - Company information, leadership, and affiliated pages
- **Job postings** - Job search results and detailed job page data
- **Articles** - LinkedIn article content and engagement metrics

## 📊 Data Structure

### **Profile Data Format**
Each scraped profile includes:
```json
{
  "original_profile": {
    "name": "John Doe",
    "linkedin_url": "https://www.linkedin.com/in/johndoe",
    "search_keyword": "Software Engineer",
    "profession": "Software Engineer"
  },
  "scraped_data": {
    "profile": {
      "name": "John Doe",
      "headline": "Senior Software Engineer at Tech Corp",
      "location": "San Francisco, CA",
      "experience": [...],
      "education": [...],
      "skills": [...]
    },
    "posts": [...]
  },
  "scraping_timestamp": 1640995200.0,
  "batch_number": 1,
  "record_index": 0
}
```

### **Output Organization**
```
data_source/
├── linkedin_profiles_001.jsonl    # First 100,000 profiles
├── linkedin_profiles_002.jsonl    # Next 100,000 profiles
└── ...

results/
├── all_profiles.json              # Complete dataset (JSON format)
├── scraping_summary.json          # Processing statistics
└── ...
```

## 🛠️ Technical Architecture

### **Core Components**
- **`linkedin.py`** - Core scraping engine with LinkedIn-specific parsers
- **`scrape_all_profiles.py`** - Production scraper for large-scale data collection
- **`run.py`** - Example usage and testing scripts
- **`utils.py`** - Data formatting and file management utilities

### **Technology Stack**
- **Python 3.10+** - Modern Python with async/await support
- **Scrapfly SDK** - Professional web scraping infrastructure
- **Loguru** - Advanced logging and progress tracking
- **Pathlib** - Cross-platform file path management

### **Data Processing Pipeline**
1. **CSV Input** → Read profile URLs from structured CSV files
2. **Batch Processing** → Scrape profiles in configurable batches
3. **Incremental Saving** → Save data immediately as it's processed
4. **File Management** → Automatically chunk large datasets
5. **Integrity Verification** → Validate all output files
6. **Summary Generation** → Create comprehensive processing reports

## 📋 Setup and Installation

### **Prerequisites**
- Python 3.10 or higher
- Poetry package manager
- Scrapfly API key

### **Installation Steps**

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd linkedin-scraper
   ```

2. **Set up environment**
   ```bash
   # Install dependencies
   poetry install
   
   # Set your Scrapfly API key
   export SCRAPFLY_KEY="your-api-key-here"
   ```

3. **Prepare your data**
   ```bash
   # Ensure your CSV file is in the project directory
   # Format: name,linkedin_url,search_keyword,profession
   ```

##  Usage

### **Large-Scale Profile Collection**
```bash
# Scrape all profiles from your CSV file
poetry run python scrape_all_profiles.py
```

### **Example Scraping**
```bash
# Run example scrapes (small datasets)
poetry run python run.py
```

### **Testing**
```bash
# Run comprehensive tests
poetry install --with dev
poetry run pytest test.py

# Test specific components
poetry run pytest test.py -k test_profile_scraping
poetry run pytest test.py -k test_company_scraping
```

## 📈 Performance and Scalability

### **Processing Capacity**
- **Batch Size**: Configurable (default: 10 profiles per batch)
- **File Limits**: 100,000 records per JSONL file
- **Memory Efficiency**: Streams data to disk, doesn't load everything in memory
- **Error Recovery**: Continues processing even with individual failures

### **Expected Performance**
- **601 profiles**: ~60-90 minutes (with rate limiting)
- **Success Rate**: 85-95% (varies based on profile accessibility)
- **Output**: 1-2 JSONL files (depending on success rate)

## 🔒 Data Quality and Compliance

### **Quality Assurance**
- **JSONL Validation**: Every record is validated before saving
- **File Integrity**: Complete verification of all output files
- **Error Logging**: Comprehensive logging of all failures and issues
- **Progress Tracking**: Real-time progress updates and statistics

### **Compliance Features**
- **Rate Limiting**: Respectful delays between requests
- **Error Handling**: Graceful handling of blocked or unavailable profiles
- **Data Integrity**: No partial or corrupted records in output files

## 📊 Output and Analysis

### **Generated Files**
- **JSONL Files**: Production-ready data in `data_source/` directory
- **Summary Report**: Processing statistics in `results/scraping_summary.json`
- **Log Files**: Detailed processing logs for debugging

### **Data Analysis Ready**
The output JSONL files are immediately ready for:
- **Data pipelines** and ETL processes
- **Analytics platforms** and BI tools
- **Machine learning** model training
- **Research** and academic studies

##  Contributing

This system is designed for professional use and continuous improvement. Contributions are welcome for:
- **Performance optimizations**
- **Additional data extraction capabilities**
- **Enhanced error handling**
- **New output formats**

## 📄 License

This project is developed for professional data collection and research purposes. Please ensure compliance with LinkedIn's terms of service and applicable data protection regulations.

## ⚠️ Important Notes

- **Rate Limiting**: The system includes built-in delays to respect LinkedIn's servers
- **Data Usage**: Ensure compliance with LinkedIn's terms of service
- **API Limits**: Monitor your Scrapfly usage and plan accordingly
- **Backup**: Always backup your CSV input files before processing

---

**Built for professionals who need reliable, scalable LinkedIn data collection.**