import os
from pathlib import Path

import pandas as pd
import snowflake.connector


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"

SNOWFLAKE_ACCOUNT = "FD58066.ap-south-1.aws"
SNOWFLAKE_USER = "ahmedkhalidse8"
SNOWFLAKE_DATABASE = "ECOMMERCE_ANALYTICS"
SNOWFLAKE_SCHEMA = "RAW"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_ROLE = "ACCOUNTADMIN"


# ============================================================
# Snowflake connection
# ============================================================

def get_connection():

    password = os.getenv("SNOWFLAKE_PASSWORD")

    if not password:
        raise ValueError(
            "SNOWFLAKE_PASSWORD environment variable is not set."
        )

    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=password,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        role=SNOWFLAKE_ROLE,
    )


# ============================================================
# Load CSV into Snowflake
# ============================================================

def load_table(connection, csv_name, table_name):

    filepath = PROCESSED_DIR / csv_name

    print("=" * 60)
    print(f"Loading {csv_name}...")
    print("=" * 60)

    if not filepath.exists():
        raise FileNotFoundError(
            f"File not found: {filepath}"
        )

    df = pd.read_csv(filepath)

    print(f"Local rows: {len(df)}")

    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # Create temporary staging table
        # ----------------------------------------------------

        stage_table = f"{table_name}_LOAD"

        cursor.execute(
            f"DROP TABLE IF EXISTS {stage_table}"
        )

        # Let Snowflake infer the CSV structure through
        # pandas -> executemany style inserts.
        #
        # For this first automated pipeline version,
        # we create the table explicitly based on the
        # processed CSV columns.

        if table_name == "ORDERS":

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ORDERS (
                    order_id VARCHAR,
                    order_date TIMESTAMP_TZ,
                    order_status VARCHAR,
                    payment_status VARCHAR,
                    seller_id VARCHAR,
                    item_id VARCHAR,
                    line_item_id VARCHAR,
                    title VARCHAR,
                    quantity NUMBER,
                    line_item_price FLOAT,
                    order_total FLOAT,
                    delivery_cost FLOAT,
                    total_due_seller FLOAT,
                    currency VARCHAR
                )
            """)

        elif table_name == "TRAFFIC":

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS TRAFFIC (
                    date DATE,
                    impressions NUMBER,
                    views NUMBER,
                    transactions NUMBER,
                    conversion_rate FLOAT
                )
            """)

        elif table_name == "INVENTORY":

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS INVENTORY (
                    sku VARCHAR,
                    title VARCHAR,
                    description VARCHAR,
                    quantity NUMBER,
                    condition VARCHAR
                )
            """)

        else:
            raise ValueError(
                f"Unknown table: {table_name}"
            )

        # ----------------------------------------------------
        # Replace current RAW data
        # ----------------------------------------------------

        cursor.execute(
            f"TRUNCATE TABLE {table_name}"
        )

        # ----------------------------------------------------
        # Prepare rows
        # ----------------------------------------------------

        rows = []

        for row in df.itertuples(index=False, name=None):
            rows.append(
                tuple(
                    None if pd.isna(value) else value
                    for value in row
                )
            )

        # ----------------------------------------------------
        # Insert data
        # ----------------------------------------------------

        placeholders = ", ".join(
            ["%s"] * len(df.columns)
        )

        insert_sql = f"""
            INSERT INTO {table_name}
            VALUES ({placeholders})
        """

        cursor.executemany(
            insert_sql,
            rows
        )

        connection.commit()

        # ----------------------------------------------------
        # Verify
        # ----------------------------------------------------

        cursor.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        )

        snowflake_rows = cursor.fetchone()[0]

        print(f"Snowflake rows: {snowflake_rows}")

        if snowflake_rows != len(df):

            raise RuntimeError(
                f"Row count mismatch for {table_name}: "
                f"local={len(df)}, "
                f"snowflake={snowflake_rows}"
            )

        print(
            f"SUCCESS: {table_name} loaded successfully."
        )
        print()

    finally:

        cursor.close()


# ============================================================
# Main pipeline
# ============================================================

def main():

    print()
    print("=" * 60)
    print("STARTING SNOWFLAKE LOAD")
    print("=" * 60)
    print()

    connection = get_connection()

    try:

        load_table(
            connection,
            "orders.csv",
            "ORDERS"
        )

        load_table(
            connection,
            "traffic.csv",
            "TRAFFIC"
        )

        load_table(
            connection,
            "inventory.csv",
            "INVENTORY"
        )

        print("=" * 60)
        print("SNOWFLAKE LOAD COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()

    finally:

        connection.close()


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    main()