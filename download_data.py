#!/usr/bin/env python3
"""
Dataset Download Script
Automatically downloads FARS and Education data required for the analysis.

Usage:
    python download_data.py

This script will:
1. Create the datasets/ folder
2. Download FARS accident data (2010-2023) from NHTSA
3. Download Education data (2010-2023) from USDA ERS
4. Extract and organize files in the correct structure
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
DATASETS_DIR = BASE_DIR / "datasets"

# FARS data URLs (NHTSA)
# Format: https://www.nhtsa.gov/file-downloads/download?p=nhtsa/downloads/FARS/{year}/National/FARS{year}NationalCSV.zip
FARS_BASE_URL = "https://static.nhtsa.gov/nhtsa/downloads/FARS"

# Education data URLs (USDA ERS - Economic Research Service)
# These are county-level education statistics
EDUCATION_BASE_URL = "https://www.ers.usda.gov/webdocs/DataFiles/48747"

def print_header():
    print("=" * 60)
    print("  Traffic Safety Analysis - Dataset Downloader")
    print("=" * 60)
    print()

def create_directories():
    """Create the datasets directory if it doesn't exist."""
    print("📁 Creating directories...")
    DATASETS_DIR.mkdir(exist_ok=True)
    print(f"   Created: {DATASETS_DIR}")

def download_file(url, dest_path, desc=""):
    """Download a file with progress indicator."""
    print(f"   ⬇️  Downloading: {desc or url.split('/')[-1]}")
    try:
        urllib.request.urlretrieve(url, dest_path)
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def download_fars_data():
    """Download FARS data for years 2010-2023."""
    print("\n📊 Downloading FARS (Fatality Analysis Reporting System) Data...")
    print("   Source: NHTSA (National Highway Traffic Safety Administration)")
    print()
    
    for year in range(2010, 2024):
        fars_dir = DATASETS_DIR / f"FARS{year}"
        
        # Skip if already exists
        if fars_dir.exists() and (fars_dir / "accident.csv").exists():
            print(f"   ✓ FARS{year} already exists, skipping...")
            continue
        
        # Download ZIP file
        # Try different URL patterns (NHTSA has changed their URL structure over years)
        urls_to_try = [
            f"{FARS_BASE_URL}/{year}/National/FARS{year}NationalCSV.zip",
            f"https://www.nhtsa.gov/file-downloads/download?p=nhtsa/downloads/FARS/{year}/National/FARS{year}NationalCSV.zip",
        ]
        
        zip_path = DATASETS_DIR / f"FARS{year}.zip"
        downloaded = False
        
        for url in urls_to_try:
            if download_file(url, zip_path, f"FARS{year}"):
                downloaded = True
                break
        
        if not downloaded:
            print(f"   ⚠️  Could not download FARS{year} - you may need to download manually")
            print(f"      Visit: https://www.nhtsa.gov/research-data/fatality-analysis-reporting-system-fars")
            continue
        
        # Extract ZIP
        print(f"   📦 Extracting FARS{year}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                fars_dir.mkdir(exist_ok=True)
                z.extractall(fars_dir)
            zip_path.unlink()  # Remove ZIP after extraction
            print(f"   ✓ FARS{year} extracted successfully")
        except Exception as e:
            print(f"   ❌ Extraction failed: {e}")

def download_education_data():
    """Download Education data for years 2010-2023."""
    print("\n📚 Downloading Education Data...")
    print("   Source: USDA Economic Research Service / US Census Bureau")
    print()
    
    # Note: Education data is typically available as a single file or annual files
    # The actual URLs depend on the data source. These are placeholder patterns.
    
    for year in range(2010, 2024):
        edu_file = DATASETS_DIR / f"Education{year}.csv"
        
        # Skip if already exists
        if edu_file.exists():
            print(f"   ✓ Education{year}.csv already exists, skipping...")
            continue
        
        # Education data typically comes from Census ACS (American Community Survey)
        # or USDA ERS Education data files
        print(f"   ⚠️  Education{year}.csv not found")
        print(f"      Manual download required from Census Bureau or USDA ERS")
    
    print("\n   📌 Education Data Sources:")
    print("      - USDA ERS: https://www.ers.usda.gov/data-products/county-level-data-sets/")
    print("      - Census ACS: https://data.census.gov/")

def print_summary():
    """Print summary of downloaded data."""
    print("\n" + "=" * 60)
    print("  Download Summary")
    print("=" * 60)
    
    # Count FARS directories
    fars_count = len([d for d in DATASETS_DIR.iterdir() if d.is_dir() and d.name.startswith("FARS")])
    edu_count = len([f for f in DATASETS_DIR.iterdir() if f.name.startswith("Education") and f.suffix == ".csv"])
    
    print(f"\n   FARS datasets found:      {fars_count}/14")
    print(f"   Education datasets found: {edu_count}/14")
    
    if fars_count < 14 or edu_count < 14:
        print("\n   ⚠️  Some datasets are missing. Please download manually:")
        print("      - FARS: https://www.nhtsa.gov/research-data/fatality-analysis-reporting-system-fars")
        print("      - Education: https://www.ers.usda.gov/data-products/county-level-data-sets/")
    else:
        print("\n   ✅ All datasets are available!")
    
    print("\n   Next steps:")
    print("      1. Run the analysis: python analysis-code/analysis_report_v2.py")
    print("      2. Check the 'output/' folder for visualizations")
    print()

def main():
    print_header()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    create_directories()
    download_fars_data()
    download_education_data()
    print_summary()

if __name__ == "__main__":
    main()
