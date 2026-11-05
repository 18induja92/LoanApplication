import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# SQL Schema Definitions
SCHEMA = """
-- Applications table - stores loan applications
CREATE TABLE IF NOT EXISTS applications (
    id TEXT PRIMARY KEY,
    applicant_id TEXT NOT NULL,
    age INTEGER,
    income DECIMAL,
    employment_type TEXT,
    credit_score INTEGER,
    loan_amount DECIMAL,
    tenure_months INTEGER,
    existing_liabilities DECIMAL,
    location TEXT,
    application_timestamp DATETIME,
    status TEXT DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Decisions table - stores final loan decisions
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    classification TEXT NOT NULL,
    risk_score DECIMAL,
    confidence_level DECIMAL,
    reasoning TEXT,
    key_decision_factors TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);

-- Audit logs table - compliance and action tracking
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    case_id TEXT,
    application_id TEXT,
    agent_name TEXT,
    action TEXT,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_applications_applicant_id ON applications(applicant_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_decisions_application_id ON decisions(application_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_application_id ON audit_logs(application_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_case_id ON audit_logs(case_id);
"""


def get_connection(database_path: str) -> sqlite3.Connection:
    """Get a connection to the SQLite database"""
    try:
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise


def initialize_database(database_path: str) -> bool:
    """Initialize the database with schema"""
    try:
        # Create parent directory if it doesn't exist
        db_path = Path(database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = get_connection(database_path)
        cursor = conn.cursor()

        # Execute schema
        for statement in SCHEMA.split(";"):
            if statement.strip():
                cursor.execute(statement)

        conn.commit()
        logger.info(f"Database initialized successfully at {database_path}")
        return True

    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        return False
    finally:
        if conn:
            conn.close()


def drop_all_tables(database_path: str) -> bool:
    """Drop all tables (for testing purposes)"""
    try:
        conn = get_connection(database_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = cursor.fetchall()

        # Drop each table
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")

        conn.commit()
        logger.info("All tables dropped successfully")
        return True

    except sqlite3.Error as e:
        logger.error(f"Error dropping tables: {e}")
        return False
    finally:
        if conn:
            conn.close()


def reset_database(database_path: str) -> bool:
    """Reset database by dropping and recreating all tables"""
    logger.info("Resetting database...")
    if drop_all_tables(database_path):
        return initialize_database(database_path)
    return False


def check_database_health(database_path: str) -> dict:
    """Check the health of the database"""
    health = {
        "status": "unknown",
        "tables": [],
        "error": None,
    }

    try:
        conn = get_connection(database_path)
        cursor = conn.cursor()

        # Check if tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        health["tables"] = tables
        health["status"] = "healthy" if tables else "empty"

        # Get row counts
        counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]

        health["row_counts"] = counts
        return health

    except sqlite3.Error as e:
        health["status"] = "error"
        health["error"] = str(e)
        logger.error(f"Error checking database health: {e}")
        return health
    finally:
        if conn:
            conn.close()
