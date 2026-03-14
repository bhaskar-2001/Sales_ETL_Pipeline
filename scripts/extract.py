import pandas as pd
import os

def extract_data(filepath="data/sales_raw.csv"):
    df = pd.read_csv(filepath)
    print(f"Extracted {len(df)} rows from {filepath}")
    return df