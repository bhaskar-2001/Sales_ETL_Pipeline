import pandas as pd

def transform_data(df):

    before = len(df)

    # 1. Remove exact duplicates
    df = df.drop_duplicates()

    # 2. Fix mixed date formats (handles both YYYY-MM-DD and DD/MM/YYYY)
    df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=False, errors="coerce")
    df = df.dropna(subset=["order_date"])

    # 3. Drop rows with missing critical fields
    df = df.dropna(subset=["product", "price"])
    df["customer_name"] = df["customer_name"].fillna("Unknown Customer")
    df["city"] = df["city"].fillna("Unknown City")

    # 4. Remove negative or zero quantities (data entry errors)
    df = df[df["quantity"] > 0]

    # 5. Ensure correct data types
    df["quantity"] = df["quantity"].astype(int)
    df["price"] = df["price"].astype(float)
    df["order_id"] = df["order_id"].astype(int)

    # 6. Remove duplicate order_ids (keep first occurrence)
    df = df.drop_duplicates(subset=["order_id"], keep="first")

    # 7. Standardise text casing
    df["customer_name"] = df["customer_name"].str.strip().str.title()
    df["city"] = df["city"].str.strip().str.title()
    df["product"] = df["product"].str.strip().str.title()

    # 8. Create calculated column
    df["total_sales"] = df["quantity"] * df["price"]

    # 9. Add date parts for the dimension table
    df["month"] = df["order_date"].dt.month
    df["year"] = df["order_date"].dt.year

    after = len(df)
    print(f"Cleaned data: {before} → {after} rows ({before - after} removed)")
    return df