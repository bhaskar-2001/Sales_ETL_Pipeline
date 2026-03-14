import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from extract import extract_data
from transform import transform_data
from load import load_data

def run_pipeline():
    print("=== ETL Pipeline Starting ===")
    df = extract_data()
    df = transform_data(df)
    load_data(df)
    print("=== Pipeline Completed Successfully ===")

if __name__ == "__main__":
    run_pipeline()