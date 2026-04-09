# OTIF Engine

An order fulfillment tracking system that calculates and monitors On-Time In-Full (OTIF) metrics for supply chain operations. Integrates data from multiple sources (Redshift, SharePoint, AWS) to provide unified visibility into delivery performance.

## Features

- **Multi-source data integration**: Consolidates data from Redshift databases, SharePoint, CSV files, and AWS Parameter Store
- **Flexible data fetching**: Supports both tabular data and Excel mappings with multi-threaded ingestion
- **Status computation**: Calculates OTIF metrics and delivery status tracking
- **Automated scheduling**: Daily data refreshes with intelligent date handling (skips weekends)
- **Secure credential management**: AWS Parameter Store integration for credential storage

## Tech Stack

- **Data Processing**: Python, pandas, numpy
- **Database**: Amazon Redshift
- **Cloud**: AWS (S3, Parameter Store, boto3)
- **SharePoint**: Microsoft SharePoint with certificate-based authentication
- **Excel**: openpyxl, xlsxwriter
- **Development**: Jupyter notebooks for analysis and testing

## Setup

1. **Install dependencies**:
   ```bash
   pip install pandas numpy openpyxl xlsxwriter redshift-connector boto3 msal requests
   ```

2. **Configure credentials**:
   - Store AWS credentials in AWS Parameter Store (recommended) or environment variables
   - Avoid hardcoding credentials in version control
   - Use `creds.txt` format only for local development (excluded from git)

3. **Configure data sources**:
   - Update SharePoint URLs and API settings
   - Configure Redshift connection parameters
   - Map local CSV files in `Testing Setup/local_data_dnd/`

## Usage

```python
from Testing_Setup.ingestion_tables_multithreading import fetch_from_redshift
from Testing_Setup.ingestion_excels import main
from src.data_fetcher import fetch_all_data

# Fetch data from configured sources
dfs_tables = {...}  # Load from Redshift
dfs_excels = {...}  # Load from SharePoint/local Excel files

# Consolidate all data
consolidated_data = fetch_all_data(dfs_tables, dfs_excels)
```

## Project Structure

- `src/` - Core modules (data fetcher, formatter, transformers, status computation)
- `Testing Setup/` - Data ingestion scripts and test datasets
- `configs/` - Configuration files (status rules, mappings)
- `main.py` - Entry point for OTIF calculation

## Notes

- Large CSV test datasets are excluded from version control
- Credentials should be managed via AWS Parameter Store in production
- Multi-threading is used for efficient data fetching from large sources