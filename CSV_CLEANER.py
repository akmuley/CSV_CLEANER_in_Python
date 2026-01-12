from pathlib import Path
import argparse
import csv
from datetime import datetime
from collections import Counter


#Fucntion for Reading CSV file

def read_csv(path):
    """Read the csv file and return the data as List of rows (each row is dict of column and value"""
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, headers):

    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow({h: r.get(h, "") for h in headers})


def strip_spaces(row):
    """Remove white spaces from the data . """
    cleaned = []
    for r in row:
        cleaned.append({k:(v.strip() if isinstance(v,str) else v) for k, v in r.items()})
    return cleaned

def drop_rows_with_missing_values(rows,req_cols):

    """ this function will remove the ros where null values are present in required columns where were
    shared as argument """

    if not req_cols:
        return rows

    keep=[]

    for r in rows:
        if all(r.get(c,"").strip() != "" for c in req_cols):
            """looping through all items and return true if all are correct else will return false even when 
            one value is incorrect  """
            keep.append(r)
    return keep

def normalise_dates(rows,dates_col):

    """ changing the format of the date for YYYY-MM-DD if the date is passed in any of the below 3 formats -
    %Y-%m-%d  or %d/%m/%Y or %m/%d/%Y  , also added new column to the dictionary data_valid and setting
    valid to yes if date is formatted  correctly , else no"""

    if not dates_col:
        return rows

    result =[]
    for r in rows:
        val = r.get(dates_col,"")
        temp = "yes"
        if val:
            parsed = None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
                try:
                    parsed = datetime.strptime(val, fmt)
                    break
                except Exception:
                    pass
            if parsed:
                r[dates_col] = parsed.strftime("%Y-%m-%d")
            else:
                temp="no"
        else:
            temp = "no"

        r["date_valid"] = temp
        result.append(r)
    return result

def summarize(rows, category_col, stat_cols) :
    """
    Build a basic summary:
    - row count
    - sums and averages as per the stats col provided
    - top 5 categories (if category_col is provided)

    Returns:
        (row_count, sums, avgs, top_categories)
    """
    row_count = len(rows)
    sums = {}
    avgs = {}

    if isinstance(stat_cols, str):
        stat_cols = [stat_cols]

    for c in stat_cols:
        s = 0.0
        n = 0
        for r in rows:
            v = r.get(c, "").strip()
            #print(v)
            if v != "":
                try:
                    s += float(v)
                    n += 1
                except Exception:
                    pass
        if n > 0:
            sums[c] = round(s, 2)
            avgs[c] = round(s / n, 2)

    top_cats = []
    if category_col:
        counts = Counter([r.get(category_col, "").strip() for r in rows if r.get(category_col)])
        top_cats = counts.most_common(5)

    return row_count, sums, avgs, top_cats



def main():
    """ CSV cleaner Project """
    parser = argparse.ArgumentParser(
        prog="CSV file Cleaner",
        description="Program to clean CSV file"
    )
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    parser.add_argument("--required-cols", help=" Comma seperated required columns eg (id,name)")
    parser.add_argument("--date-col", help="Column if date needs to be normalised (optional)")
    parser.add_argument("--category-col", help="Name of a category column to show top values (optional)")
    parser.add_argument("--print-summary", action="store_true", help="Print summary to console")
    parser.add_argument("--stats-col", help="Name of the column of which sum and avg is required ")

    args = parser.parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)

    #print("Input file path is :",in_path)
    #print("Output File path is :",out_path)

    if not in_path.exists():
        raise SystemExit(f"Input file {in_path} doesnt exists.")

    rows = read_csv(in_path)
    rows = strip_spaces(rows)  #Removing blankspaces if any from the data either at start or at end


    req_cols = [c.strip() for c in (args.required_cols or "").split(",") if c.strip()]

    #print(args.required_cols)
    #print("Columsn are - ",req_cols)

    """dropping rows where value is null for required cols passed in argument"""
    rows = drop_rows_with_missing_values(rows,req_cols)

    """"change the date format to YYYY-MM-DD"""
    rows = normalise_dates(rows, args.date_col)

    headers = list(rows[0].keys()) if rows else []

    #print("hearder value is ", headers)
    #print("rows are :",rows )
    write_csv(out_path, rows, headers)

    stat_cols = [c.strip() for c in (args.stats_col or "").split(",") if c.strip()]

    if args.print_summary:
        row_count, sums, avgs, top_cats = summarize(rows, args.category_col, stat_cols)
        print("--- Summary ---")
        print(f"Rows (after cleaning): {row_count}")
        if sums:
            print("Numeric sums:", sums)
        if avgs:
            print("Numeric avgs:", avgs)
        if top_cats:
            print(f"Top categories for '{args.category_col}':", top_cats)
        print(f"Cleaned file saved to: {out_path}")

if __name__ == "__main__":
    main()