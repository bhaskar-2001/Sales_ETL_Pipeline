import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)

def load_data(df):
    engine = get_engine()

    with engine.connect() as conn:
        # Drop in reverse dependency order so foreign keys don't block us
        conn.execute(text("TRUNCATE TABLE fact_sales RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_customer RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_product RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_date RESTART IDENTITY CASCADE"))
        conn.commit()

    # --- dim_customer ---
    customers = df[["customer_name", "city"]].drop_duplicates().reset_index(drop=True)
    customers.to_sql("dim_customer", engine, if_exists="append", index=False, method="multi")

    # --- dim_product ---
    products = df[["product", "price"]].drop_duplicates().reset_index(drop=True)
    products = products.rename(columns={"product": "product_name"})
    products.to_sql("dim_product", engine, if_exists="append", index=False, method="multi")

    # --- dim_date ---
    dates = df[["order_date", "month", "year"]].drop_duplicates().reset_index(drop=True)
    dates.to_sql("dim_date", engine, if_exists="append", index=False, method="multi")

    # --- fact_sales (join back to get surrogate keys) ---
    with engine.connect() as conn:
        cust_map = pd.read_sql("SELECT customer_id, customer_name, city FROM dim_customer", conn)
        prod_map = pd.read_sql("SELECT product_id, product_name FROM dim_product", conn)
        date_map = pd.read_sql("SELECT date_id, order_date FROM dim_date", conn)

    date_map["order_date"] = pd.to_datetime(date_map["order_date"])
    df = df.rename(columns={"product": "product_name"})

    fact = df.merge(cust_map, on=["customer_name", "city"])
    fact = fact.merge(prod_map, on="product_name")
    fact = fact.merge(date_map, on="order_date")

    fact = fact[["order_id", "customer_id", "product_id", "date_id", "quantity", "total_sales"]]
    fact.to_sql("fact_sales", engine, if_exists="append", index=False, method="multi")

    print(f"Loaded {len(fact)} rows into fact_sales")
    print("Dimension tables: dim_customer, dim_product, dim_date")