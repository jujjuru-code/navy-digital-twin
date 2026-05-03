# Navy Sailor Digital Twin POC

This POC demonstrates the Sailor Digital Twin vision for MyNavy HR.

## Stack
- Python 3.10+, SQLite, Streamlit, pandas
- All data is synthetic; no PII anywhere in this project

## Project conventions
- Schema lives in src/schema.sql
- All data generation patterns are in src/generate_data.py
- The Streamlit app is src/app.py — feature engineering and scoring logic live here
- Database file is data/navy_dt.db; regenerate with `python generate_data.py` from src/

## When making changes
- Match Navy source-system field names (NSIPS, TFMMS, NTMPS, MRRS) where possible
- Preserve the "Sailor at the center" data model — every domain joins to sailor.dod_id
- Update the data_model.md design doc when changing the schema