# scripts/create_sample_db.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    region TEXT NOT NULL,
    product TEXT NOT NULL,
    units_sold INTEGER NOT NULL,
    revenue REAL NOT NULL
);

DELETE FROM sales;

INSERT INTO sales (month, region, product, units_sold, revenue) VALUES
    ('January',   'North', 'Widget A', 120, 6000.00),
    ('January',   'South', 'Widget B',  95, 4750.00),
    ('January',   'East',  'Widget A',  80, 4000.00),
    ('January',   'West',  'Widget C', 110, 7700.00),
    ('February',  'North', 'Widget B', 140, 7000.00),
    ('February',  'South', 'Widget A', 100, 5000.00),
    ('February',  'East',  'Widget C',  90, 6300.00),
    ('February',  'West',  'Widget A', 130, 6500.00),
    ('March',     'North', 'Widget C', 160, 11200.00),
    ('March',     'South', 'Widget B', 115, 5750.00),
    ('March',     'East',  'Widget A', 105, 5250.00),
    ('March',     'West',  'Widget B',  85, 4250.00),
    ('April',     'North', 'Widget A',  75, 3750.00),
    ('April',     'South', 'Widget C', 125, 8750.00),
    ('April',     'East',  'Widget B', 145, 7250.00),
    ('April',     'West',  'Widget A',  95, 4750.00);
""")

conn.commit()
conn.close()
print(f"✅ Sample database created at: {os.path.abspath(DB_PATH)}")
