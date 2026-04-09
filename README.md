# OTIF Engine

A Python-based data integration and calculation engine for computing On-Time In-Full (OTIF) metrics in supply chain operations. The engine consolidates data from multiple sources (Redshift databases, SharePoint, AWS Parameter Store) and applies business logic to calculate fulfillment performance indicators.

## Key Features

- **Multi-source data integration**: Fetches data from Redshift, SharePoint, and local CSV files
- **Multithreaded ingestion**: Efficient parallel data fetching using ThreadPoolExecutor
- **Data consolidation**: Maps and merges data from purchase orders, invoices, compliance records, and supply chain tables
- **Flexible configuration**: Status rules and mappings managed via JSON and Excel files
- **AWS integration**: Secure credential management via AWS Parameter Store and IAM

## Tech Stack

- **Core**: Python 3, pandas, NumPy
- **Database**: Redshift (redshift_connector)
- **Cloud**: AWS (boto3, Parameter Store)
- **Integration**: SharePoint (msal, requests)
- **Data Processing**: openpyxl, xlsxwriter, xlwings
- **Utilities**: pytz, xlsxwriter

## Setup

1. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install pandas numpy redshift-connector boto3 msal openpyxl xlsxwriter xlwings requests pytz
   ```

3. **Configure credentials**:
   - Store AWS credentials and SharePoint secrets in AWS Parameter Store under:
     - `/sharepoint_automations/client` (JSON: SharePoint client config)
     - `/sharepoint_automations/secrets` (JSON: private key, thumbprint)
   - Alternatively, create a `creds.txt` file with format:
     ```
     AWS_ACCESS_KEY_ID=your_key
     AWS_SECRET_ACCESS_KEY=your_secret
     REDSHIFT_USER=your_user
     REDSHIFT_PASSWORD=your_password
     ```

4. **Prepare test data**:
   - Place CSV files in `Testing Setup/local_data_dnd/` (excels and tables subdirectories)
   - Configure mappings in Excel files or local CSVs

## Usage

```python
from Testing Setup.ingestion_tables_multithreading import fetch_from_redshift
from Testing Setup.ingestion_excels import main as fetch_from_sharepoint
from src.data_fetcher import fetch_all_data

# Fetch data from sources
po_data = fetch_from_redshift(user_id, password, database, host, port, sql_query)
excel_mappings = fetch_from_sharepoint(root_url, relative_url, tracker, sheet)

# Consolidate and compute OTIF
dfs_tables = {'po_data': po_data, ...}
dfs_excels = {'status_mapping': mappings, ...}
result = fetch_all_data(dfs_tables, dfs_excels)
```

## Project Structure

```
otif_engine/
├── main.py                 # Entry point
├── src/
│   ├── data_fetcher.py     # Data extraction module
│   ├── data_formatter.py   # Data formatting
│   ├── data_transformers.py # Data transformation
│   ├── status_computation.py # OTIF status logic
│   └── utils/
│       └── expression_evaluator.py
├── Testing Setup/          # Data ingestion and testing
│   ├── ingestion_tables_multithreading.py
│   ├── ingestion_excels.py
│   ├── sharepoint.py
│   └── local_data_dnd/     # Reference CSV data
├── configs/
│   └── status_rules.json   # Business rule configurations
├── development_practices.md
└── project_brain.md
```

## Notes

- This is an in-development project with some modules still in planning phase
- Test data files are large (up to 2.3 MB) and are excluded from version control
- Credentials should be managed via AWS Parameter Store in production