# Sales ETL Pipeline

An end-to-end data engineering pipeline that extracts raw sales data from CSV, cleans and transforms it using Python and Pandas, loads it into a PostgreSQL star schema (via Docker), and visualises it in a Power BI dashboard — with automated execution via GitHub Actions.

---

## Architecture

```
sales_raw.csv
      │
      ▼
 extract.py          → reads raw CSV into Pandas DataFrame
      │
      ▼
 transform.py        → cleans, fixes types, removes bad rows
      │
      ▼
 load.py             → builds star schema, loads into PostgreSQL
      │
      ▼
 PostgreSQL (Docker) → dim_customer, dim_product, dim_date, fact_sales
      │
      ▼
 Power BI            → KPI dashboard connected live to PostgreSQL
      │
      ▼
 GitHub Actions      → automates pipeline on every push
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Data processing | Pandas, NumPy |
| Database | PostgreSQL 15 (Docker) |
| DB admin | pgAdmin 4 (Docker) |
| ORM / connector | SQLAlchemy + psycopg2 |
| Visualisation | Power BI Desktop |
| Automation | GitHub Actions |
| Environment | Ubuntu (pipeline) + Windows (Power BI) |

---

## Project Structure

```
sales-etl-pipeline/
│
├── data/
│   └── sales_raw.csv            # raw input data (not tracked in git)
│
├── scripts/
│   ├── extract.py               # reads CSV into DataFrame
│   ├── transform.py             # data cleaning & transformation
│   ├── load.py                  # loads star schema into PostgreSQL
│   └── etl_pipeline.py          # orchestrates extract → transform → load
│
├── sql/
│   └── schema.sql               # PostgreSQL star schema DDL
│
├── outputs/                     # cleaned exports (not tracked in git)
│
├── .github/
│   └── workflows/
│       └── etl.yml              # GitHub Actions CI workflow
│
├── docker-compose.yml           # PostgreSQL + pgAdmin containers
├── requirements.txt             # Python dependencies
├── .env                         # credentials (not tracked in git)
└── README.md
```

---

## Data Cleaning

The raw dataset (`10,700 rows`) contains several quality issues that the pipeline handles automatically:

| Issue | Fix applied |
|---|---|
| Mixed date formats (`YYYY-MM-DD` and `DD/MM/YYYY`) | `pd.to_datetime` with `dayfirst=False` |
| Missing product names | rows dropped |
| Missing customer / city names | filled with `"Unknown"` |
| Null prices | rows dropped |
| Negative quantities | rows filtered out |
| Duplicate `order_id` values | first occurrence kept |
| Inconsistent text casing | `.str.title()` applied |

After cleaning: **~9,882 rows** loaded into the database.

---

## Star Schema

```
             dim_customer
             (customer_id, customer_name, city)
                    │
                    │
dim_product ────── fact_sales ────── dim_date
(product_id,       (order_id,        (date_id,
 product_name,      customer_id,      order_date,
 price)             product_id,       month,
                    date_id,          year)
                    quantity,
                    total_sales)
```

---

## Quick Start

### Prerequisites

- Docker + Docker Compose installed on Ubuntu
- Python 3.10+ with `venv`
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/sales-etl-pipeline.git
cd sales-etl-pipeline
```

### 2. Set up Python environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_etl
DB_USER=etl_user
DB_PASSWORD=yourpassword
```

### 4. Start PostgreSQL and pgAdmin via Docker

```bash
docker compose up -d
```

- PostgreSQL available at `localhost:5432`
- pgAdmin available at `http://localhost:5050`
  - Email: `admin@etl.com`
  - Password: `admin123`

### 5. Add your raw data

```bash
cp /path/to/sales_dataset.csv data/sales_raw.csv
```

### 6. Run the pipeline

```bash
python scripts/etl_pipeline.py
```

Expected output:
```
=== ETL Pipeline Starting ===
Extracted 10700 rows from data/sales_raw.csv
Cleaned data: 10700 → 9882 rows (818 removed)
Loaded 9882 rows into fact_sales
=== Pipeline Completed Successfully ===
```

### 7. Verify in pgAdmin

Open `http://localhost:5050`, connect to `sales_postgres`, and confirm the four tables under `sales_etl → Schemas → public → Tables`.

---

## Power BI Dashboard

Power BI runs on Windows and connects live to the PostgreSQL instance running in Docker on Ubuntu (same local network).

**Connection settings in Power BI:**
- Server: `<ubuntu-local-ip>:5432`
- Database: `sales_etl`

**Dashboard visuals:**
- KPI cards — Total Revenue, Total Orders, Avg Order Value
- Bar chart — Revenue by city
- Line chart — Monthly sales trend
- Donut chart — Sales by product category
- Table — Top customers by revenue
- Slicer — Filter by year

---

## GitHub Actions CI

The pipeline runs automatically on every push to `main` and on a daily schedule (midnight UTC).

GitHub Actions spins up its own isolated `postgres:15` service container — completely independent of your local Docker environment.

**Required GitHub secret:**

| Secret name | Value |
|---|---|
| `DB_PASSWORD` | your database password |

Add it at: `Settings → Secrets and variables → Actions → New repository secret`

---

## Key SQL Queries

```sql
-- Total revenue
SELECT SUM(total_sales) AS total_revenue FROM fact_sales;

-- Revenue by city
SELECT c.city, SUM(f.total_sales) AS revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.city ORDER BY revenue DESC;

-- Top 5 products by units sold
SELECT p.product_name, SUM(f.quantity) AS units_sold
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_name ORDER BY units_sold DESC LIMIT 5;

-- Monthly sales trend
SELECT d.year, d.month, SUM(f.total_sales) AS monthly_sales
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.year, d.month ORDER BY d.year, d.month;
```

---

## Dependencies

```
pandas
numpy
sqlalchemy
psycopg2-binary
python-dotenv
```

Install with:
```bash
pip install -r requirements.txt
```

---

## .gitignore

The following are excluded from version control:

```
venv/
.env
data/sales_raw.csv
outputs/
__pycache__/
*.pyc
.vscode/
```

---

## Interview Summary

> "I built an end-to-end ETL pipeline using Python and Pandas to process 10,000+ rows of raw sales data. The pipeline performs automated data cleaning — handling mixed date formats, null values, negative quantities, and duplicate records — then loads structured data into a PostgreSQL star schema running in Docker. I connected the data warehouse to Power BI to build a live KPI dashboard for sales analysis. The pipeline is version-controlled on GitHub and fully automated using GitHub Actions CI."
