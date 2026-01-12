
# CSV Data Cleaner & Summary (Python)

Python script to clean a CSV file and print a simple summary.
- Removes extra spaces
- Checks required columns
- Normalizes a date column (YYYY-MM-DD)
- Summarizes numeric columns and shows top categories

## Run
```bash
python csv_cleaner.py --input sample.csv --output cleaned.csv   --required-cols id,name   --date-col order_date   --category-col category   --print-summary --stats-col amount
```

## Test
```bash
pip install -r requirements.txt
```

## Run Tests
```bash
python -m pytest cleaner_tests.py 
```

## Why I built this
To practice Python basics: file handling, validation, simple calculations, and unit tests.
