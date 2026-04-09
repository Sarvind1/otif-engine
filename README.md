# OTIF Engine

A Python-based supply chain data consolidation and OTIF (On-Time In-Full) stage calculation engine. Ingests order, inventory, and shipment data from Redshift, applies status mappings and business rules from SharePoint, and computes fulfillment metrics.

## Features

- **Multi-source data integration**: Aggregates data from Redshift, SharePoint, and AWS Parameter Store
- **Multithreaded ingestion**: Efficiently fetches large datasets from Redshift using ThreadPoolExecutor
- **Flexible mappings**: Status, blocker, payment term, and vendor mappings loaded from SharePoint
- **Modular architecture**: Separate modules for data fetching, formatting, and transformation
- **Local testing setup**: Comprehensive local data fixtures for development and testing

## Tech Stack

- **Python 3.x**
- **Data Processing**: pandas, numpy
- **Database**: redshift_connector (AWS Redshift)
- **Cloud**: boto3 (AWS), msal (Microsoft authentication)
- **Excel/Spreadsheets**: openpyxl, xlsxwriter, xlwings
- **SharePoint Integration**: requests, msal

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install pandas numpy redshift-connector openpyxl xlsxwriter boto3 msal requests xlwings
   ```
4. Configure credentials:
   - Set up `creds.txt` with Redshift and AWS credentials (excluded from version control)
   - Alternatively, use AWS Parameter Store for secure credential management
5. Update SharePoint URLs and paths in configuration

## Usage

```python
from src.data_fetcher import fetch_all_data

# Fetch consolidated data
consolidated_df = fetch_all_data(dfs_tables, dfs_excels, debug=True)

# Process with transformers and status computation
# See src/data_transformers.py and src/status_computation.py
```

## Project Structure

```
├── src/
│   ├── data_fetcher.py           # Core data aggregation
│   ├── data_formatter.py         # Data formatting utilities
│   ├── data_transformers.py      # Business logic transformations
│   ├── status_computation.py     # OTIF stage calculations
│   └── utils/
│       └── expression_evaluator.py
├── Testing Setup/               # Test data and ingestion scripts
│   ├── ingestion_tables_multithreading.py
│   ├── ingestion_excels.py
│   ├── sharepoint.py
│   └── local_data_dnd/          # Local test fixtures
├── configs/
│   └── status_rules.json        # Status mapping rules
└── main.py                       # Entry point
```

## Notes

- Large CSV files and test data are excluded from version control
- Credentials and secrets are never committed
- Use environment variables or AWS Parameter Store for production credentials