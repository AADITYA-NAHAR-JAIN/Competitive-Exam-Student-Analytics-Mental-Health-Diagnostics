import os
import shutil
import pandas as pd

# Import modules from src
import sys
sys.path.append('src')

from utils import auto_load_dataset, generate_overview_report
from data_cleaning import DataCleaner
from eda import EDAAnalyzer
from dashboard import build_dashboard
from make_reports import generate_word_report, generate_pdf_report, generate_readme, generate_requirements


def main():
    print("=" * 70)
    print("      AUTONOMOUS AI DATA ANALYST - MASTER PIPELINE EXECUTION")
    print("=" * 70)

    # Setup directories
    directories = ['data', 'cleaned_data', 'visuals', 'dashboard', 'reports', 'presentation', 'notebooks', 'src']
    for d in directories:
        os.makedirs(d, exist_ok=True)

    # Copy raw data into data/
    raw_data_file = 'data.csv.csv'
    if os.path.exists(raw_data_file):
        shutil.copy(raw_data_file, os.path.join('data', 'raw_dataset.csv'))

    # Copy core python scripts to root as well as src for multi-location access
    for script in ['utils.py', 'data_cleaning.py', 'eda.py', 'dashboard.py']:
        src_script = os.path.join('src', script)
        if os.path.exists(src_script):
            shutil.copy(src_script, script)

    # PHASE 1: Dataset Loading & Overview
    print("\n[PHASE 1] Loading Dataset & Detecting Format...")
    df_raw = auto_load_dataset(raw_data_file)
    overview = generate_overview_report(df_raw, raw_data_file)
    print(f"Dataset Loaded: {overview['num_rows']} rows, {overview['num_cols']} columns ({overview['memory_usage_mb']} MB)")

    # PHASE 2 & 3: Data Quality Assessment & Intelligent Cleaning
    print("\n[PHASE 2 & 3] Data Quality Assessment & Intelligent Cleaning...")
    cleaner = DataCleaner(raw_data_file)
    cleaner.load_data()
    quality_report = cleaner.assess_quality()
    df_cleaned = cleaner.clean_data()
    cleaned_path, scaled_path = cleaner.export_datasets()

    # PHASE 4: Exploratory Data Analysis & Statistical Testing
    print("\n[PHASE 4] Exploratory Data Analysis & Statistical Testing...")
    eda = EDAAnalyzer(df_cleaned)
    eda.run_univariate_analysis()
    eda.run_bivariate_analysis()
    eda.run_multivariate_analysis()
    stats_results = eda.perform_statistical_tests()
    print("Statistical Analysis Completed Successfully.")

    # INTERACTIVE DASHBOARD GENERATION
    print("\n[BUILD] Generating Interactive Plotly Dashboard...")
    build_dashboard(df_cleaned)

    # EXECUTIVE & BUSINESS REPORTS GENERATION
    print("\n[BUILD] Generating Formal Documentation Reports...")
    generate_word_report(df_cleaned)
    generate_pdf_report(df_cleaned)
    generate_readme()
    generate_requirements()

    print("\n" + "=" * 70)
    print("      ALL DELIVERABLES SUCCESSFULLY CREATED & DEPLOYED!")
    print("=" * 70)
    print("Root Deliverables Checklist:")
    for item in ['cleaned_dataset.csv', 'scaled_dataset.csv', 'dashboard.html', 
                 'executive_report.pdf', 'business_report.docx', 
                 'README.md', 'requirements.txt']:
        status = "✓ EXISTS" if os.path.exists(item) else "✗ MISSING"
        print(f"  - {item}: {status}")


if __name__ == '__main__':
    main()
