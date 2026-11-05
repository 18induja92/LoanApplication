#!/usr/bin/env python3
"""
Script to initialize the database with schema
Run this once before starting the application
"""

import sys
import logging
from config.settings import DATABASE_PATH, logger
from database import initialize_database, check_database_health


def main():
    logger.info("Starting database initialization...")

    # Initialize database
    if initialize_database(DATABASE_PATH):
        logger.info("✓ Database initialized successfully")
    else:
        logger.error("✗ Failed to initialize database")
        return False

    # Check database health
    health = check_database_health(DATABASE_PATH)
    logger.info(f"Database Health: {health['status']}")
    logger.info(f"Tables: {', '.join(health['tables'])}")

    logger.info("✓ Database setup complete!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
