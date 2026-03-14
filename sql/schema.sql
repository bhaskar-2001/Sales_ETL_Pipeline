CREATE TABLE IF NOT EXISTS dim_customer (
  customer_id SERIAL PRIMARY KEY,
  customer_name VARCHAR(100),
  city VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_product (
  product_id SERIAL PRIMARY KEY,
  product_name VARCHAR(100),
  price NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS dim_date (
  date_id SERIAL PRIMARY KEY,
  order_date DATE,
  month INT,
  year INT
);

CREATE TABLE IF NOT EXISTS fact_sales (
  order_id INT PRIMARY KEY,
  customer_id INT REFERENCES dim_customer(customer_id),
  product_id INT REFERENCES dim_product(product_id),
  date_id INT REFERENCES dim_date(date_id),
  quantity INT,
  total_sales NUMERIC(12,2)
);