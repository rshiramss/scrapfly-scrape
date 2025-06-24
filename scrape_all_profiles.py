"""
Script to scrape all LinkedIn profiles from the CSV file.
This script reads the CSV file containing LinkedIn profile URLs and scrapes each profile.

STRICT ADHERENCE TO JSONL PROTOCOL:
- Each line is a complete, valid JSON object
- No commas between lines, only newlines
- All strings use double quotes
- Each record is atomic and independent
- INCREMENTAL SAVING: Saves complete files as scraping progresses

To run this script set the env variable $SCRAPFLY_KEY with your scrapfly API key:
$ export $SCRAPFLY_KEY="your key from https://scrapfly.io/dashboard"
"""

import asyncio
import json
import csv
import time
from pathlib import Path
from typing import List, Dict
import linkedin
from loguru import logger as log

# Setup output directories
output = Path(__file__).parent / "results"
output.mkdir(exist_ok=True)
data_output = Path(__file__).parent / "data_source"
data_output.mkdir(exist_ok=True)

def read_csv_profiles(csv_file: str) -> List[Dict]:
    """Read LinkedIn profile URLs from CSV file"""
    profiles = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Ensure all values are properly formatted strings
                profiles.append({
                    "name": str(row["name"]).strip(),
                    "linkedin_url": str(row["linkedin_url"]).strip(),
                    "search_keyword": str(row["search_keyword"]).strip(),
                    "profession": str(row["profession"]).strip()
                })
        log.success(f"Loaded {len(profiles)} profiles from CSV file")
        return profiles
    except Exception as e:
        log.error(f"Error reading CSV file: {e}")
        return []

def validate_jsonl_record(record: Dict) -> bool:
    """Validate that a record follows JSONL protocol"""
    try:
        # Test that the record can be serialized to JSON
        json_str = json.dumps(record, ensure_ascii=False)
        # Test that it can be deserialized back
        json.loads(json_str)
        return True
    except Exception:
        return False

class IncrementalJSONLSaver:
    """Handles incremental saving of scraped data to JSONL files"""
    
    def __init__(self, output_dir: Path, prefix: str = "linkedin_profiles", chunk_size: int = 100000):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.prefix = prefix
        self.chunk_size = chunk_size
        self.current_chunk = 1
        self.current_file_records = 0
        self.total_records_saved = 0
        self.current_file_path = None
        self.current_file_handle = None
        
        # Start the first file
        self._start_new_file()
    
    def _start_new_file(self):
        """Start a new JSONL file"""
        if self.current_file_handle:
            self.current_file_handle.close()
        
        filename = f"{self.prefix}_{self.current_chunk:03d}.jsonl"
        self.current_file_path = self.output_dir / filename
        self.current_file_handle = open(self.current_file_path, "w", encoding="utf-8")
        self.current_file_records = 0
        
        log.info(f"Started new file: {filename}")
    
    def save_record(self, record: Dict) -> bool:
        """Save a single record to the current JSONL file"""
        try:
            # Validate the record
            if not validate_jsonl_record(record):
                log.warning(f"Invalid JSONL record, skipping")
                return False
            
            # Check if we need to start a new file
            if self.current_file_records >= self.chunk_size:
                log.info(f"File limit reached ({self.chunk_size} records), starting new file")
                self._start_new_file()
                self.current_chunk += 1
            
            # Write the record to the current file
            json_line = json.dumps(record, ensure_ascii=False)
            self.current_file_handle.write(json_line + "\n")
            self.current_file_handle.flush()  # Ensure data is written immediately
            
            self.current_file_records += 1
            self.total_records_saved += 1
            
            return True
            
        except Exception as e:
            log.error(f"Error saving record: {e}")
            return False
    
    def close(self):
        """Close the current file and finalize"""
        if self.current_file_handle:
            self.current_file_handle.close()
            self.current_file_handle = None
            
        log.success(f"Saved {self.total_records_saved} total records across {self.current_chunk} files")
    
    def get_file_info(self):
        """Get information about created files"""
        files = list(self.output_dir.glob(f"{self.prefix}_*.jsonl"))
        return {
            "total_files": len(files),
            "total_records": self.total_records_saved,
            "files": sorted([f.name for f in files])
        }

async def scrape_profiles_in_batches(profiles: List[Dict], saver: IncrementalJSONLSaver, batch_size: int = 10) -> int:
    """Scrape profiles in batches and save incrementally"""
    total_profiles = len(profiles)
    successful_scrapes = 0
    
    log.info(f"Starting to scrape {total_profiles} profiles in batches of {batch_size}")
    
    for i in range(0, total_profiles, batch_size):
        batch = profiles[i:i + batch_size]
        batch_urls = [profile["linkedin_url"] for profile in batch]
        
        log.info(f"Scraping batch {i//batch_size + 1}/{(total_profiles + batch_size - 1)//batch_size} "
                f"({len(batch)} profiles)")
        
        try:
            # Scrape the batch
            scraped_data = await linkedin.scrape_profile(batch_urls)
            
            # Process and save each scraped profile immediately
            batch_success_count = 0
            for j, profile_data in enumerate(scraped_data):
                if profile_data:  # Only process if scraping was successful
                    # Create atomic record following JSONL protocol
                    combined_data = {
                        "original_profile": batch[j],
                        "scraped_data": profile_data,
                        "scraping_timestamp": time.time(),
                        "batch_number": i//batch_size + 1,
                        "record_index": i + j
                    }
                    
                    # Save the record immediately
                    if saver.save_record(combined_data):
                        batch_success_count += 1
                        successful_scrapes += 1
            
            log.success(f"Successfully scraped and saved {batch_success_count} profiles from batch")
            
            # Add a small delay between batches to be respectful to the API
            if i + batch_size < total_profiles:
                log.info("Waiting 2 seconds before next batch...")
                await asyncio.sleep(2)
                
        except Exception as e:
            log.error(f"Error scraping batch {i//batch_size + 1}: {e}")
            continue
    
    log.success(f"Completed scraping. Total successful scrapes: {successful_scrapes}/{total_profiles}")
    return successful_scrapes

def verify_jsonl_integrity(output_dir: Path, prefix: str, expected_total: int):
    """Verify that all JSONL files are valid and contain the expected number of records"""
    log.info("Verifying JSONL file integrity...")
    
    total_lines = 0
    chunk_files = list(output_dir.glob(f"{prefix}_*.jsonl"))
    
    for chunk_file in sorted(chunk_files):
        chunk_lines = 0
        try:
            with open(chunk_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:  # Skip empty lines
                        # Verify each line is valid JSON
                        json.loads(line)
                        chunk_lines += 1
                        
                        # Verify line starts with { and ends with }
                        if not (line.startswith("{") and line.endswith("}")):
                            log.error(f"Invalid JSONL format in {chunk_file}:{line_num}")
                            raise ValueError(f"Line {line_num} is not a complete JSON object")
            
            total_lines += chunk_lines
            log.success(f"Verified {chunk_file.name}: {chunk_lines} valid records")
            
        except Exception as e:
            log.error(f"Error verifying {chunk_file}: {e}")
            raise
    
    if total_lines != expected_total:
        log.error(f"Data integrity check failed: expected {expected_total} records, found {total_lines}")
        raise ValueError(f"Record count mismatch: expected {expected_total}, found {total_lines}")
    
    log.success(f"JSONL integrity verification passed: {total_lines} records across {len(chunk_files)} files")

async def main():
    """Main function to orchestrate the scraping process"""
    # Enable scrapfly cache and debug
    linkedin.BASE_CONFIG["cache"] = False
    linkedin.BASE_CONFIG["debug"] = True
    
    # CSV file path
    csv_file = "raw_links_20250623_191239.csv"
    
    print(f"Starting LinkedIn profile scraping from {csv_file}")
    print("Results will be saved incrementally to ./data_source directory in strict JSONL format")
    
    # Read profiles from CSV
    profiles = read_csv_profiles(csv_file)
    if not profiles:
        print("No profiles found in CSV file. Exiting.")
        return
    
    # Initialize the incremental saver
    saver = IncrementalJSONLSaver(data_output, prefix="linkedin_profiles", chunk_size=100000)
    
    try:
        # Scrape all profiles with incremental saving
        start_time = time.time()
        successful_scrapes = await scrape_profiles_in_batches(profiles, saver, batch_size=10)
        end_time = time.time()
        
        # Close the saver to finalize files
        saver.close()
        
        if successful_scrapes > 0:
            # Get file information
            file_info = saver.get_file_info()
            
            # Verify data integrity
            verify_jsonl_integrity(data_output, "linkedin_profiles", successful_scrapes)
            
            # Create summary statistics
            summary = {
                "total_profiles_in_csv": len(profiles),
                "successfully_scraped": successful_scrapes,
                "success_rate": f"{(successful_scrapes / len(profiles) * 100):.2f}%",
                "scraping_time_seconds": round(end_time - start_time, 2),
                "professions_breakdown": {},
                "jsonl_files_created": file_info
            }
            
            # Count professions (we need to read the files to get this info)
            profession_counts = {}
            for file_path in data_output.glob("linkedin_profiles_*.jsonl"):
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            record = json.loads(line)
                            profession = record["original_profile"]["profession"]
                            profession_counts[profession] = profession_counts.get(profession, 0) + 1
            
            summary["professions_breakdown"] = profession_counts
            
            # Save summary
            with open(output.joinpath("scraping_summary.json"), "w", encoding="utf-8") as file:
                json.dump(summary, file, indent=2, ensure_ascii=False)
            
            print(f"\nScraping completed successfully!")
            print(f"Total profiles in CSV: {len(profiles)}")
            print(f"Successfully scraped: {successful_scrapes}")
            print(f"Success rate: {summary['success_rate']}")
            print(f"Time taken: {summary['scraping_time_seconds']} seconds")
            print(f"JSONL files created in: {data_output}")
            
            # List created files
            for file_name in file_info["files"]:
                print(f"  - {file_name}")
            
        else:
            print("No profiles were successfully scraped.")
            
    except KeyboardInterrupt:
        log.warning("Scraping interrupted by user. Saving current progress...")
        saver.close()
        print("Current progress has been saved. You can resume from where you left off.")
        
    except Exception as e:
        log.error(f"Unexpected error during scraping: {e}")
        saver.close()
        print("Error occurred, but current progress has been saved.")

if __name__ == "__main__":
    asyncio.run(main())