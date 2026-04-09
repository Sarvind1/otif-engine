# Project Brain - OTIF Stage Calculation Engine

**Author**: Sarvind

## Project Overview
OTIF (On Time In Full) stage calculation engine for tracking and managing purchase order lifecycle stages. The system processes multiple data sources to calculate current status, sub-status, and responsibility assignments for each PO line.

## Current File Structure
```
otif_engine/
├── project_brain.md          # Project documentation and knowledge base
├── main.py                   # Main entry point
├── src/
│   ├── data_fetcher.py      # Extract relevant datapoints from dataframes
│   ├── data_formatter.py    # Format data into primary datapoints
│   ├── data_transformers.py # Transform primary data to derived datapoints
│   ├── status_computation.py # Calculate status using JSON rules
│   └── utils/
│       └── expression_evaluator.py # Dynamic expression evaluation
└── configs/
    └── status_rules.json    # Business logic configuration
```

## Architecture Components

### 1. Data Fetching Module
**Purpose**: Extract and consolidate all data sources into a single unified dataframe
- **Input Sources**:
  - Database tables (via `dfs_tables`)
  - Excel files (via `dfs_excels`)
- **Key Tables**:
  - `po_data`: Core purchase order information (base dataframe)
  - `pl_data`: Packing list data
  - `batch_data`: Batch-level information
  - `inb_data`: Inbound shipment data
  - Various support tables for compliance, payments, etc.
- **Implementation**:
  - Single module: `data_fetcher.py`
  - Entry point: `fetch_all_data(dfs_tables, dfs_excels, debug=False)`
  - Pure extraction and mapping - no business logic
  - Returns consolidated dataframe with all mapped columns
  - Debug mode for tracing data flow

### 2. Data Formatting Layer
**Primary Datapoints**: Standardized fields extracted directly from source data
- Date fields: `prd`, `planned_prd`, `confirmed_crd`, `quality_control_date`
- Identifiers: `document_number`, `item`, `asin`, `batch_id`
- Status fields: `production_status`, `quality_control_status`
- Key relationships: `po_razin`, `po_razin_id`, `razin_mp`, `asin_mp`

### 3. Data Transformers
**Transformed Datapoints**: Calculated fields derived from primary datapoints
- **Payment Type Logic**:
  - Line Payment Type: Based on PI/CI/BL percentages
  - Batch/INB Payment Type: Aggregated based on batch/shipment groupings
- **Status Calculations**:
  - Batch Pickup Status: Complex logic involving multiple date fields
  - Shipping Status: Based on INB# and actual shipping dates
  - Compliance Status: Mapped from external compliance data
- **Date Calculations**:
  - Estimated OTIF Delivery Date: Waterfall calculation based on available dates
  - Max QC Date: Latest QC date within a batch

### 4. Status Computation Engine
**Configuration-Driven Logic**: JSON-based rules for status determination
- **Pending Status Columns**: 31 distinct checkpoint statuses (A-D prefixes for blockers, 01-31 for process stages)
- **Current Status**: First "Yes" value in the pending columns sequence
- **Sub-Status**: Detailed breakdown with specific conditions
- **Responsibility Assignment**: Maps to accountable teams/individuals

## Key Business Logic Patterns

### 1. Waterfall Logic
Used extensively for date calculations and status determinations:
```python
def waterfall_calculation(row):
    if condition1:
        return value1
    elif condition2:
        return value2
    else:
        return default_value
```

### 2. Batch Aggregation
Many statuses aggregate at batch level (most restrictive wins):
```python
def batch_aggregation(row, po_data, field):
    filtered = po_data[po_data['batch_id'] == row['batch_id']][field]
    if (filtered == 'Restrictive Value').any():
        return 'Restrictive Value'
    else:
        return row[field]
```

### 3. Conditional Mapping
Status mappings based on multiple conditions:
```python
status = map_value if condition else alternative_map[key]
```

## Critical Data Dependencies

### 1. Batch ID
- Central grouping mechanism
- Drives aggregated calculations
- Missing batch_id defaults to line-level logic

### 2. INB# (Inbound Number)
- Links to shipment tracking
- Triggers shipping/delivery statuses
- Required for telex release logic

### 3. Payment Terms
- PI/CI/BL percentages drive payment flow
- BL Days special handling for deferred payments
- Invoice submission gates payment approval

## Status Flow Hierarchy

1. **Pre-Production**: PO approval → Supplier confirmation → PI handling
2. **Production**: PRD setting → Under production → Ready for batching
3. **Pre-Shipment**: Batch creation → QC → Booking → Pickup
4. **In-Transit**: INB creation → Shipping → Telex release
5. **Delivery**: Stock receiving → PO closing

## Expression Evaluator Integration
The `expression_evaluator.py` module enables:
- Dynamic date calculations: `max(date1, date2)`, `add_days(date, 5)`
- Conditional logic: `cond(status == 'Approved', date1, date2)`
- Stage references: `stage_01 + 5` (references to calculated values)

## Performance Considerations

### 1. DataFrame Operations
- Avoid iterative lookups in apply functions
- Pre-compute mapping dictionaries
- Use vectorized operations where possible

### 2. Memory Management
- Process data in chunks for large datasets
- Clear intermediate dataframes
- Use appropriate data types (int vs float, category for strings)

### 3. Debugging Strategy
- Implement debug mode flags
- Add strategic print statements
- Log calculation steps for complex logic

## Common Pitfalls & Solutions

### 1. Date Handling
- **Issue**: Mixed date formats, timezone issues
- **Solution**: Standardize to datetime objects early, handle timezones explicitly

### 2. Missing Data
- **Issue**: NaN, empty strings, "NA" values
- **Solution**: Consistent null checking, use fillna strategically

### 3. Circular Dependencies
- **Issue**: Status A depends on Status B which depends on Status A
- **Solution**: Clear hierarchy, break circular refs with intermediate calculations

## Future Enhancement Opportunities

1. **Configuration Management**:
   - Move all business rules to JSON configs
   - Version control for rule changes
   - A/B testing for rule modifications

2. **Performance Optimization**:
   - Parallel processing for independent calculations
   - Caching for expensive lookups
   - Database query optimization

3. **Monitoring & Alerting**:
   - Track calculation performance
   - Alert on data quality issues
   - Dashboard for status distribution

## Testing Strategy

### 1. Unit Tests
- Individual transformer functions
- Expression evaluator edge cases
- Date calculation scenarios

### 2. Integration Tests
- Full pipeline with sample data
- Batch aggregation logic
- Status transition validation

### 3. Data Quality Tests
- Required field validation
- Referential integrity checks
- Business rule compliance