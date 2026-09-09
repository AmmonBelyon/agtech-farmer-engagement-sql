import duckdb

# 1. Connect to an in-memory DuckDB sandbox
con = duckdb.connect(database=':memory:')

# 2. Register the local CSV files directly as SQL tables
# 2. Register the local CSV files directly as SQL tables using absolute paths
con.execute("CREATE TABLE farmers AS SELECT * FROM 'C:/Users/Belyon_The_Earl/OneDrive/Desktop/farmers.csv';")
con.execute("CREATE TABLE transactions AS SELECT * FROM 'C:/Users/Belyon_The_Earl/OneDrive/Desktop/transactions.csv';")


print("⚡ Local Data Sandboxed! Running Exploratory SQL Queries...\n")
print("="*70)

# -------------------------------------------------------------------------
# QUERY 1: Regional Churn & Infrastructure Bottlenecks
# -------------------------------------------------------------------------
print("\n📊 INSIGHT 1: Regional Farmer Churn Rates (60+ Days Inactive)")
query_1 = """    WITH last_interaction AS (
        SELECT 
            farmer_id,
            MAX(transaction_date) as last_tx_date
        FROM transactions
        GROUP BY 1
    )
    SELECT 
        f.region,
        COUNT(f.farmer_id) as total_farmers,
        COUNT(CASE WHEN ('2026-09-09'::DATE - li.last_tx_date) > 60 THEN 1 END) as inactive_farmers,
        ROUND(
            (COUNT(CASE WHEN ('2026-09-09'::DATE - li.last_tx_date) > 60 THEN 1 END)::NUMERIC / 
            COUNT(f.farmer_id)::NUMERIC) * 100, 2
        ) as churn_rate_pct
    FROM farmers f
    LEFT JOIN last_interaction li ON f.farmer_id = li.farmer_id
    GROUP BY 1
    ORDER BY churn_rate_pct DESC;
"""
print(con.execute(query_1).df().to_string(index=False))
print("-" * 70)

# -------------------------------------------------------------------------
# QUERY 2: Economic Value Generation Per Hectare (SDG 8 Indicator)
# -------------------------------------------------------------------------
print("\n🌾 INSIGHT 2: Top 5 Highest Yielding Regional Crop Segments (KES/Hectare)")
query_2 = """    SELECT 
        f.region,
        f.primary_crop,
        SUM(f.farm_size_hectares) as total_hectares,
        SUM(CASE WHEN t.transaction_type = 'Crop Sale Payout' THEN t.amount_kes ELSE 0 END) as total_payouts_kes,
        ROUND(
            SUM(CASE WHEN t.transaction_type = 'Crop Sale Payout' THEN t.amount_kes ELSE 0 END) / 
            SUM(f.farm_size_hectares), 2
        ) as kes_payout_per_hectare
    FROM farmers f
    JOIN transactions t ON f.farmer_id = t.farmer_id
    GROUP BY 1, 2
    HAVING total_hectares > 0
    ORDER BY kes_payout_per_hectare DESC
    LIMIT 5;
"""
print(con.execute(query_2).df().to_string(index=False))
print("-" * 70)

# -------------------------------------------------------------------------
# QUERY 3: Marketplace Wallet Utilization & Capital Flow
# -------------------------------------------------------------------------
print("\n💳 INSIGHT 3: FinTech Platform Capital Spend (Input Purchase Velocity)")
query_3 = """    SELECT 
        f.region,
        COUNT(CASE WHEN t.transaction_type = 'Input Purchase' THEN 1 END) as input_purchases,
        SUM(CASE WHEN t.transaction_type = 'Input Purchase' THEN t.amount_kes ELSE 0 END) as input_spend_kes,
        ROUND(AVG(CASE WHEN t.transaction_type = 'Input Purchase' THEN t.amount_kes END), 2) as avg_input_cost_kes
    FROM farmers f
    JOIN transactions t ON f.farmer_id = t.farmer_id
    GROUP BY 1
    ORDER BY input_spend_kes DESC;
"""
print(con.execute(query_3).df().to_string(index=False))
print("="*70)
