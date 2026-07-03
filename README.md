# Competitive Exam Student Analytics & Mental Health Diagnostics

An end-to-end, consulting-grade data analysis project analyzing student stress, study behaviors, sleep deprivation, and performance metrics across competitive entrance exam candidates.

Delivered with modern corporate design aesthetics matching top consulting firms (McKinsey, Deloitte, PwC).

https://competitive-exam-student-analytics-gilt.vercel.app/


## 🛠 Tech Stack

- **Core & Manipulation**: Python 3.13, Pandas, NumPy
- **Exploratory Visualizations**: Matplotlib, Seaborn, Missingno
- **Interactive Dashboard**: Plotly HTML
- **Statistical Analysis**: SciPy, Scikit-Learn
- **Deliverable Generation**: `python-pptx` (PowerPoint), `python-docx` (Word), `reportlab` (PDF)

## 📁 Project Directory Structure

```
project/
│
├── data/                    # Raw input data directory
├── cleaned_data/            # Processed CSV & scaled feature datasets
├── visuals/                 # High-resolution (300 DPI) exported chart figures
├── dashboard/               # Interactive Plotly dashboard HTML assets
├── reports/                 # Executive PDF & DOCX formal reports
├── presentation/            # Professional PowerPoint slide deck
├── notebooks/               # Jupyter exploration workspace
├── src/                     # Modular Python pipeline source scripts
│   ├── utils.py             # Global constants, file loaders & styling utilities
│   ├── data_cleaning.py     # Data quality assessment & cleaning pipeline
│   ├── eda.py               # Univariate, bivariate, multivariate & stats testing
│   └── dashboard.py         # Plotly interactive dashboard generator
├── cleaned_dataset.csv      # Root deliverable: Cleaned tabular dataset
├── scaled_dataset.csv       # Root deliverable: Standardized feature dataset
├── dashboard.html           # Root deliverable: Standalone interactive dashboard
├── executive_report.pdf     # Root deliverable: Executive PDF summary
├── business_report.docx     # Root deliverable: Detailed Word business report
├── presentation.pptx        # Root deliverable: 10-Slide Corporate PowerPoint
├── run_pipeline.py          # Master orchestrator execution script
├── README.md                # Project documentation
└── requirements.txt         # Package dependency specification
```

## 🚀 Execution Instructions

To run the full autonomous data analysis pipeline and recreate all deliverables:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run master pipeline execution script
python3 run_pipeline.py
```

## 📊 Key Analytical Highlights

- **Acute Stress Epidemic**: Over **62.4%** of candidates experience high daily stress (≥8/10).
- **Sleep Deprivation Link**: Statistically verified inverse relationship between sleep duration and stress levels (T-Test p < 0.05).
- **Institutional Void**: **100%** of surveyed students reported zero access to formal counseling support at their coaching centers.

---
*Created by AI Data Analyst Autonomous Agent.*
