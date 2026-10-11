"""
Initialize Enterprise SQLite Database for Multi-Agent Planning & Orchestration.
Contains tables: departments, quarterly_revenue, sales_deals, customer_churn, audit_claims.
"""

import sqlite3
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DATA_DIR, "enterprise_database.sqlite")

def init_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Departments Table
    cursor.execute("""
    CREATE TABLE departments (
        dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        division TEXT NOT NULL,
        head TEXT NOT NULL,
        headcount INTEGER NOT NULL,
        annual_budget_usd REAL NOT NULL
    );
    """)

    departments_data = [
        ("AI Platforms", "Core Engineering", "Dr. Clara Zhao", 42, 14500000.0),
        ("Cloud Infrastructure", "Systems & Ops", "Bob Martin", 58, 12200000.0),
        ("Enterprise Sales", "Go-To-Market", "Sarah Jenkins", 75, 18000000.0),
        ("Product & Design", "Product", "David Kumar", 34, 8500000.0),
        ("Customer Success", "Customer Experience", "Elena Rostova", 46, 6800000.0),
        ("Financial Strategy", "Corporate Operations", "Fiona Gallagher", 22, 5400000.0)
    ]
    cursor.executemany("INSERT INTO departments (name, division, head, headcount, annual_budget_usd) VALUES (?, ?, ?, ?, ?);", departments_data)

    # 2. Quarterly Revenue Table
    cursor.execute("""
    CREATE TABLE quarterly_revenue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quarter TEXT NOT NULL,
        fiscal_year INTEGER NOT NULL,
        revenue_millions REAL NOT NULL,
        target_millions REAL NOT NULL,
        operating_cost_millions REAL NOT NULL,
        ebitda_millions REAL NOT NULL
    );
    """)

    quarterly_data = [
        ("Q1", 2024, 48.5, 45.0, 31.2, 17.3),
        ("Q2", 2024, 54.2, 52.0, 34.0, 20.2),
        ("Q3", 2024, 61.8, 60.0, 38.5, 23.3),
        ("Q4", 2024, 72.4, 70.0, 43.1, 29.3),
        ("Q1", 2025, 68.2, 75.0, 46.0, 22.2),
        ("Q2", 2025, 79.5, 80.0, 49.8, 29.7),
        ("Q3", 2025, 88.0, 85.0, 52.4, 35.6),
        ("Q4", 2025, 102.5, 95.0, 58.2, 44.3)
    ]
    cursor.executemany("INSERT INTO quarterly_revenue (quarter, fiscal_year, revenue_millions, target_millions, operating_cost_millions, ebitda_millions) VALUES (?, ?, ?, ?, ?, ?);", quarterly_data)

    # 3. Enterprise Sales Deals Table
    cursor.execute("""
    CREATE TABLE sales_deals (
        deal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        industry TEXT NOT NULL,
        region TEXT NOT NULL,
        deal_size_usd REAL NOT NULL,
        stage TEXT NOT NULL,
        close_quarter TEXT NOT NULL,
        account_executive TEXT NOT NULL
    );
    """)

    deals_data = [
        ("Apex BioTech", "Healthcare", "North America", 1450000.0, "Closed-Won", "2025-Q1", "Marcus Vance"),
        ("HyperScale FinTech", "Finance", "North America", 3800000.0, "Closed-Won", "2025-Q2", "Marcus Vance"),
        ("Nordic Telecom", "Telecommunications", "EMEA", 2100000.0, "Closed-Won", "2025-Q2", "Sonya Lindqvist"),
        ("Tokyo Data Systems", "Cloud Compute", "APAC", 2950000.0, "Closed-Won", "2025-Q3", "Kenji Sato"),
        ("AeroSpace Dynamics", "Defense & Aerospace", "North America", 4600000.0, "Closed-Won", "2025-Q4", "Marcus Vance"),
        ("Global Logistics Corp", "Supply Chain", "EMEA", 1850000.0, "Under Review", "2025-Q4", "Sonya Lindqvist"),
        ("OmniRetail Group", "Retail", "North America", 1200000.0, "Negotiation", "2026-Q1", "Marcus Vance"),
        ("Bavarian Auto Tech", "Automotive", "EMEA", 3400000.0, "Proposal", "2026-Q1", "Sonya Lindqvist")
    ]
    cursor.executemany("INSERT INTO sales_deals (client_name, industry, region, deal_size_usd, stage, close_quarter, account_executive) VALUES (?, ?, ?, ?, ?, ?, ?);", deals_data)

    # 4. Customer Churn Risk Table
    cursor.execute("""
    CREATE TABLE customer_churn (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        tier TEXT NOT NULL,
        annual_contract_value REAL NOT NULL,
        churn_risk_score REAL NOT NULL,
        primary_risk_factor TEXT NOT NULL,
        status TEXT NOT NULL
    );
    """)

    churn_data = [
        ("Vanguard Media", "Enterprise", 780000.0, 0.88, "High Latency SLA Violations", "Active-At-Risk"),
        ("Zenith Payments", "Enterprise", 1250000.0, 0.42, "Pricing Pressure", "Healthy"),
        ("Alpha Robotics", "Mid-Market", 350000.0, 0.91, "Missing Edge Inference SDK", "Critical Escalation"),
        ("Cascade Energy", "Enterprise", 950000.0, 0.25, "Stable Growth", "Healthy"),
        ("Pulse Health AI", "Strategic", 2100000.0, 0.74, "Competitor POC Active", "Active-At-Risk"),
        ("Matrix Telecom", "Mid-Market", 420000.0, 0.35, "Contract Renewal Approaching", "Healthy")
    ]
    cursor.executemany("INSERT INTO customer_churn (company_name, tier, annual_contract_value, churn_risk_score, primary_risk_factor, status) VALUES (?, ?, ?, ?, ?, ?);", churn_data)

    # 5. Audit Claims & Ground Truth Verification Table
    cursor.execute("""
    CREATE TABLE audit_claims (
        claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        statement TEXT NOT NULL,
        verified_truth TEXT NOT NULL,
        status TEXT NOT NULL,
        evidence_source TEXT NOT NULL
    );
    """)

    audit_data = [
        ("FY2025 Revenue Target", "FY2025 total revenue was claimed to be $400M with 60% growth.", "FY2025 actual total revenue was $338.2M (Q1: $68.2M, Q2: $79.5M, Q3: $88.0M, Q4: $102.5M).", "Discrepancy Found", "quarterly_revenue table"),
        ("North America Top Sales Rep", "Marcus Vance closed $10M+ in contracts in FY2025.", "Marcus Vance closed $9.85M across Apex BioTech ($1.45M), HyperScale FinTech ($3.8M), and AeroSpace Dynamics ($4.6M).", "Minor Discrepancy", "sales_deals table"),
        ("AI Platforms Headcount", "AI Platforms department has 42 members led by Dr. Clara Zhao.", "AI Platforms headcount verified at 42 members led by Dr. Clara Zhao with $14.5M annual budget.", "Verified True", "departments table")
    ]
    cursor.executemany("INSERT INTO audit_claims (subject, statement, verified_truth, status, evidence_source) VALUES (?, ?, ?, ?, ?);", audit_data)

    conn.commit()
    conn.close()
    print(f"Enterprise database initialized successfully at: {DB_PATH}")

if __name__ == "__main__":
    init_database()
