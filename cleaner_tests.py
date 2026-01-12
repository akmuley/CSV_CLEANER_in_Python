import csv
from pathlib import Path
import CSV_CLEANER as cc


def write_rows(tmp_csv: Path, rows, headers):
    with open(tmp_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def test_strip_and_required(tmp_path):
    tmp_csv = tmp_path / "in.csv"
    rows = [
        {"id": " 1 ", "name": " Alice ", "amount": " 10.0 ", "category": "Groceries"},
        {"id": "", "name": "Bob", "amount": "5.5", "category": "Groceries"},
    ]
    write_rows(tmp_csv, rows, headers=["id", "name", "amount", "category"])

    data = cc.read_csv(tmp_csv)
    data = cc.strip_spaces(data)
    data = cc.drop_rows_with_missing_values(data, ["id", "name"])

    assert len(data) == 1
    assert data[0]["id"] == "1"
    assert data[0]["name"] == "Alice"


def test_date_normalization_and_summary(tmp_path):
    tmp_csv = tmp_path / "in.csv"
    rows = [
        {"order_date": "2026-01-01", "amount": "10", "category": "A"},
        {"order_date": "01/02/2026", "amount": "20", "category": "A"},
        {"order_date": "bad", "amount": "5", "category": "B"},
    ]
    write_rows(tmp_csv, rows, headers=["order_date", "amount", "category"])
    data = cc.read_csv(tmp_csv)
    data = cc.normalise_dates(data, "order_date")
    assert {"date_valid"} <= set(data[0].keys())
    count, sums, avgs, top = cc.summarize(data, "category","amount")
    assert count == 3
    #print("sums is ",sums)
    #print("avgs is ",avgs)
    #print("count of row is ",count)
    #print("Top category is,",top)
    assert sums['amount'] == 35.0
    assert avgs["amount"] == 11.67
    assert top[0][0] == "A" and top[0][1] == 2
